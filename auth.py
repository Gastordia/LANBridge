import subprocess
import sys

def configure_ngrok(auth_token):
    ngrok_path = "/snap/bin/ngrok"
    configure_command = [ngrok_path, "config", "add-authtoken", auth_token]

    try:
        subprocess.run(configure_command, check=True, capture_output=True, text=True)
        print("Ngrok has been configured successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error configuring ngrok: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python configure_ngrok.py <auth_token>")
        sys.exit(1)
    
    auth_token = sys.argv[1]
    configure_ngrok(auth_token)