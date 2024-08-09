import subprocess, sys, os, getpass, logging, shutil, re, argparse
from termcolor import colored
import time
import requests
import itertools
import threading
import pyfiglet
import random

# Global variable for verbose mode
VERBOSE = False

def parse_arguments():
    parser = argparse.ArgumentParser(description="OpenVPN and Ngrok setup script")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--revert", action="store_true", help="Revert all changes made by the script")
    return parser.parse_args()

def verbose_print(message):
    if VERBOSE:
        print(colored(message, 'blue'))

def spinner(stop):
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    while not stop.is_set():
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        sys.stdout.write('\b')
        time.sleep(0.1)

def run_command_with_spinner(command, description, error_message):
    verbose_print(f"Executing command: {' '.join(command)}")
    print(colored(f"{description}...", 'yellow'))
    
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(stop_spinner,))
    spinner_thread.start()

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    stop_spinner.set()
    spinner_thread.join()
    sys.stdout.write(' ')  # Clear the spinner

    if VERBOSE:
        print(colored("Command output:", 'blue'))
        print(stdout)
        print(colored("Command errors:", 'blue'))
        print(stderr)
    
    if process.returncode != 0:
        print(colored(f"{error_message}\nError output: {stderr}", 'red'))
        sys.exit(1)
    elif "Failed to fetch" in stderr:
        print(colored(f"Warning: Some package lists failed to download. This may not be critical.\nOutput: {stderr}", 'yellow'))
    else:
        print(colored(f"{description} completed successfully.", 'green'))
    
    return stdout, stderr


# Function to check dependencies
def check_dependencies():
    dependencies = ["openvpn"]
    for dep in dependencies:
        if shutil.which(dep) is None:
            print(colored(f"{dep} is not installed. Please install it by running 'sudo apt install {dep}'.", 'red'))
            sys.exit(1)

# Function to check if file exists
def check_file_exists(filepath, description):
    if not os.path.exists(filepath):
        print(colored(f"{description} ({filepath}) does not exist.", 'red'))
        sys.exit(1)

# Function to check system resources
def check_system_resources():
    total, used, free = shutil.disk_usage("/")
    if free < 2 * 1024 * 1024 * 1024:  # Less than 2GB free
        print(colored("Insufficient disk space. At least 2GB of free space is required.", 'red'))
        sys.exit(1)

# Function to run command
def run_command(command, error_message):    
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE)
        print(colored(f"Command '{' '.join(command)}' executed successfully.", 'green'))
        return result
    except subprocess.CalledProcessError:
        print(colored(error_message, 'red'))
        sys.exit(1)

# Function to get local IP
def get_local_ip():
    result = run_command(['ip', 'route', 'get', '1'], "Failed to get local IP address.")
    return result.stdout.decode().split()[6]

# Function to get the actual username
def get_actual_username():
    return os.getenv("SUDO_USER") or os.getlogin()

def is_snap_installed():
    return shutil.which('snap') is not None

def install_snap_and_ngrok():
    run_command_with_spinner(
        ['sudo', 'DEBIAN_FRONTEND=noninteractive', 'apt', 'install', '-y', 'snapd'],
        "Installing snap",
        "Failed to install snap"
    )

    run_command_with_spinner(
        ['sudo', 'systemctl', 'start', 'snapd.service'],
        "Starting snapd service",
        "Failed to start snapd service"
    )

    print(colored("Waiting for snap to initialize...", 'yellow'))
    time.sleep(10)  # Wait for 10 seconds

    max_retries = 3
    for attempt in range(max_retries):
        try:
            run_command_with_spinner(
                ['sudo', 'snap', 'install', 'ngrok'],
                f"Installing ngrok (attempt {attempt + 1}/{max_retries})",
                "Failed to install ngrok"
            )
            return
        except subprocess.CalledProcessError:
            if attempt < max_retries - 1:
                print(colored(f"Installation failed. Retrying in 10 seconds...", 'yellow'))
                time.sleep(10)
            else:
                print(colored("Ngrok installation failed after multiple attempts. Please try installing manually.", 'red'))
                sys.exit(1)

def check_ngrok_installed():
    ngrok_path = "/snap/bin/ngrok"
    return os.path.exists(ngrok_path)

def get_ngrok_path():
    return "/snap/bin/ngrok"

def configure_ngrok(auth_token):
    configure_script = "auth.py"
    try:
        subprocess.run([sys.executable, configure_script, auth_token], check=True)
        print(colored("Ngrok has been configured successfully.", 'green'))
    except subprocess.CalledProcessError as e:
        print(colored(f"Error configuring ngrok: {e}", 'red'))
        sys.exit(1)

def start_ngrok_tunnel():
    ngrok_path = get_ngrok_path()
    process = subprocess.Popen(
        [ngrok_path, "tcp", "1194"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(5)  # Give ngrok some time to start

    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()['tunnels']
        ngrok_url = tunnels[0]['public_url']
        ngrok_host, ngrok_port = ngrok_url.replace("tcp://", "").split(":")
        return ngrok_host, ngrok_port
    except Exception as e:
        print(colored(f"Failed to get Ngrok URL: {str(e)}", 'red'))
        sys.exit(1)

def update_ovpn_file(username, ngrok_host, ngrok_port):
    ovpn_file = f"/home/{username}/{username}.ovpn"
    if os.path.exists(ovpn_file):
        with open(ovpn_file, "r") as file:
            content = file.read()
        
        # Find and replace the remote line
        content = re.sub(r'remote \S+ \S+', f'remote {ngrok_host} {ngrok_port}', content)
        
        with open(ovpn_file, "w") as file:
            file.write(content)
        
        print(colored(f"Updated {ovpn_file} with Ngrok host {ngrok_host} and port {ngrok_port}.", 'green'))
    else:
        print(colored(f"{ovpn_file} does not exist.", 'red'))

def print_recommended_config(local_ip):
    print(colored("\nRecommended Configuration:", 'cyan'))
    print(f"IP Address: {local_ip} (your local static ip address)")
    print("Public IPv4 address or hostname: 0.tcp.ngrok.io     (or 1.tcp.ngrok.io)")
    print("Do you want to enable IPv6 support (NAT)? [y/n]: n")
    print("Port choice [1-3]: 1                                (Port 1194)")
    print("Protocol [1-2]: 2                                   (TCP) (Ngrok only support TCP by default)")
    print("DNS [1-12]: 9                                       (Google or anything for your taste)")
    print("Enable compression? [y/n]: n")
    print("Customize encryption settings? [y/n]: n             (default should suffice)")
    print("Client name: ovpn name                                   (anything suffice)")
    print("Select an option [1-2]: 1                           (passwordless or password)")
    print(colored("\nPlease use these recommendations when prompted by the core.sh script.", 'yellow'))
    print(colored("Press Enter to continue...", 'green'))
    input()

def generate_random_ascii_art(text):
    fonts = pyfiglet.FigletFont.getFonts()
    font = random.choice(fonts)
    ascii_art = pyfiglet.figlet_format(text, font=font)
    return ascii_art

def revert_changes():
    print(colored("Reverting changes...", 'yellow'))

    # Stop and uninstall ngrok
    run_command_with_spinner(
        ['sudo', 'snap', 'remove', 'ngrok'],
        "Removing ngrok",
        "Failed to remove ngrok"
    )

    # Remove snap
    run_command_with_spinner(
        ['sudo', 'apt', 'remove', '--purge', 'snapd', '-y'],
        "Removing snap",
        "Failed to remove snap"
    )

    # Remove OpenVPN
    run_command_with_spinner(
        ['sudo', 'apt', 'remove', '--purge', 'openvpn', '-y'],
        "Removing OpenVPN",
        "Failed to remove OpenVPN"
    )

    # Remove configuration files
    username = get_actual_username()
    ovpn_file = f"/home/{username}/{username}.ovpn"
    if os.path.exists(ovpn_file):
        os.remove(ovpn_file)
        print(colored(f"Removed {ovpn_file}", 'green'))

    # Remove any other files or configurations created by the script
    # Add more cleanup steps here if needed

    print(colored("Revert process completed. All changes have been undone.", 'green'))

# Main function
def main():
    global VERBOSE
    args = parse_arguments()
    VERBOSE = args.verbose

    if args.revert:
        revert_changes()
        return

    verbose_print("Starting main function")

    # Generate and print random ASCII art for "LANBridge"
    ascii_art = generate_random_ascii_art("LANBridge")
    print(colored(ascii_art, 'yellow'))
    print(colored("The VPN of All Time", 'yellow'))

    check_dependencies()
    if os.geteuid() != 0:
        sys.exit("This script must be run as root!")
    check_system_resources()

    if not is_snap_installed() or not check_ngrok_installed():
        print(colored("Snap or Ngrok not found. Installing...", 'yellow'))
        install_snap_and_ngrok()
    
    if not check_ngrok_installed():
        print(colored("Ngrok installation failed. Please install manually.", 'red'))
        sys.exit(1)

    ngrok_auth_token = getpass.getpass(prompt=colored("Enter your Ngrok auth token: ", 'cyan'))
    configure_ngrok(ngrok_auth_token)

    local_ip = get_local_ip()
    os.environ['IP'] = local_ip
    username = get_actual_username()
    os.environ['CLIENT'] = username

    print_recommended_config(local_ip)

    run_command(['chmod', '+x', 'core.sh'], "Failed to make core.sh executable.")
    print(colored("Running core.sh script in interactive mode...", 'yellow'))
    try:
        subprocess.run(['./core.sh'], check=True)
    except subprocess.CalledProcessError:
        print(colored("Failed to run core.sh", 'red'))
        sys.exit(1)
    print(colored("core.sh script completed.", 'green'))

    print(colored("Starting Ngrok tunnel...", 'yellow'))
    ngrok_host, ngrok_port = start_ngrok_tunnel()
    print(colored(f"Ngrok tunnel established: {ngrok_host}:{ngrok_port}", 'green'))

    update_ovpn_file(username, ngrok_host, ngrok_port)

    ovpn_file_path = f"/home/{username}/{username}.ovpn"
    print(colored("Setup completed successfully!", 'green'))
    print(colored(f"Your OpenVPN configuration file is at: {ovpn_file_path}", 'green'))
    print(colored(f"Ngrok is forwarding to: {ngrok_host}:{ngrok_port}", 'green'))

    print(colored("Ngrok tunnel is now running. Press Ctrl+C to stop.", 'yellow'))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(colored("\nStopping Ngrok tunnel...", 'yellow'))
        subprocess.run([get_ngrok_path(), "stop"], check=True)
        print(colored("Ngrok tunnel stopped.", 'green'))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Exception occurred")
        print(colored(f"An error occurred: {e}", 'red'))
        sys.exit(1)