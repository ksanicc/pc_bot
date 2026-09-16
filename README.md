# Telegram Remote Control PC Bot

A cross-platform Telegram bot for remote PC control. Currently only for Windows and Linux on systemd

made by ksanicc and using some ai for studying

please dont blame me im only studying its my first project

## Quick Start

### 1. **Clone the repository**
```bash
git clone https://github.com/ksanicc/pc_bot
cd pc_bot
```
Create and init venv
```bash
python -m venv .venv    
source .venv/bin/activate    # Verify init with "which python" — it should point to .venv/bin/python
```
Install reqs and copy&redact .env
```bash
python -m pip install -r requirements.txt

cp .env.example .env
```

### 2. **Proxy setup**
By default, the bot is configured to use a local SOCKS5 proxy (socks5://127.0.0.1:10808).

To change proxy: Edit line 16 in main.py with your custom proxy URL.

To disable proxy: Comment out line 16 in main.py.

### 3. **Service**
To add this script in your service, just exec add_service.py
```bash
python add_service.py
```
### 4. **/win Command**
Its a bit complex thing. If you have DualBoot you can configure /win command to switch to Windows while on Linux without entering GRUB. 

**Need to mention it** the `efibootmgr -n` is a one-time command, after rebooting your order will be as it was cause of "-n" flag. For someone it would be better, either not

First of all you need to get your Windows BootOrder
```bash
sudo efibootmgr
```
For example:
```bash
sudo efibootmgr                                
[sudo] password for $USER: 
BootCurrent: 0002
Timeout: 0 seconds
BootOrder: 0002,0000,0001,0003,0004,0005
Boot0000* Windows Boot Manager
```
Then you need to change .env WIN_ORDER to your order
```bash
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
WIN_ORDER=your_win_order
```
After that, you need to include efibootmgr and systemctl to sudoers (to prevent sudo requesting a passwords for changing bootorder), by using echo + tee
```bash
echo "$USER ALL=(ALL) NOPASSWD: /usr/sbin/efibootmgr, /usr/bin/systemctl reboot" | sudo tee /etc/sudoers.d/pc_bot_nopass    # you can name "pc_bot_nopass" by whatever you want
```
Now you can freely use /win