# LANBridge: Bridge your LAN to the internet

LANBridge is a Python script that automates the setup of OpenVPN and Ngrok, creating a bridge to your local network. It automates the process of configuring a VPN server and making it accessible over the internet using Ngrok.

## What's This Sorcery?

Originally developed for those delightful moments when VPN IPSEC decides to take a break, LANBridge is also perfect for those "oops, we forgot to set up a VPN" emergencies. God forbid if CrowdStrike pushes another update that breaks everything, and you're stuck. No worries! With LANBridge, you can troubleshoot from the comfort of your home, because why deal with problems in person when you can do it in your pajamas?

## Features (or Reasons Why Your Security Team Will Have a Meltdown)

- Turns any Linux box into a VPN server
- Bypasses firewalls like they're made of paper
- Perfect for those "I need access NOW" moments
- Comes with a side of plausible deniability

## Prerequisites

- A Linux system (preferably one you're allowed to tinker with)
- Python 3.6 or higher (because we're not savages)
- Root access (sudo privileges, or a really gullible system admin)
- An Ngrok account and auth token (don't worry, it's free... for now)

## Installation

1. Clone this repository:
  - `git clone https://github.com/Gastordia/LANBridge.git`
  - `cd LANBridge`

2. For the lazy (which is most of us):
   
   Just run the script. It'll handle all the prerequisites like a doting parent.
  - `sudo python3 LANBridge.py`

3. For the impatient (because waiting is for chumps):

   If you find the installation process slower than your coffee break, run this first:
   - `sudo apt update && sudo apt install -y snapd && sudo systemctl start snapd.service && sleep 5 && sudo snap install ngrok`
  
     Then run the script.

Remember, patience is a virtue, but in the world of IT, it's also a luxury we can't always afford. Choose your installation method wisely!

## Usage

1. Run the script with sudo privileges (because go big or go home):
   - `sudo python3 LANBridge.py`

2. When prompted, add your Ngrok auth token.
   
   Don't have one? Get it from [Ngrok's website](https://dashboard.ngrok.com/get-started/your-authtoken). It's free, just like this advice.

   Also, make sure to verify your identity [here](https://dashboard.ngrok.com/settings#id-verification) to enable TCP endpoints.

4. Follow the prompts, or if you're feeling lucky (or lazy):
   - Just keep hitting enter like you're trying to skip a cutscene in a video game.
   - The script will use default options faster than you can say "I should probably read those".

### Command-line options:

- `-v` or `--verbose`: For when you want to see every excruciating detail (STILL BETA: AS INSTABLE AS MY MENTAL HEALTH)
- `--revert`: For when you realize this was a terrible idea and want to undo everything. We won't judge (much).

## A Word of Warning

Oh, and did I mention? LANBridge can also be used for offensive missions. So, if you break anything, that's on you. Speaking of breaking things, this is a beta version, so please test it in a VM first before unleashing it in production. I see you, lazy admins.

## Troubleshooting

And if you experience any bugs, for the love of all that is holy, use the issues section in the GitHub repo. It's there for a reason. Don't slide into my DMs with your problems.

## Legal Mumbo Jumbo

This script is provided as-is, without any warranties. Use at your own risk. If you get fired, arrested, or end up on the news because of this tool, that's on you. We're just here to provide the rope; what you do with it is your business.

## Contributing

Found a way to make this even more "powerful"? Great! Submit a pull request. Just remember, with great power comes great responsibility (and possibly unemployment).

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3) - see the [LICENSE](LICENSE) file for details.

What does this mean? Well, it's free software, and we're keeping it that way. You can run it, study it, change it, and distribute it. Just remember:

1. If you modify it, you must release the source code of your modifications.
2. You must license your modifications under the GPLv3.
3. You must state significant changes made to the software.

In other words, share and share alike. If you make this tool even more powerful (or dangerous), we all get to benefit. Or blame you. Whichever comes first.

For the full legal mumbo-jumbo, check out [https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html). It's a thrilling read, perfect for those sleepless nights wondering about software licenses.
