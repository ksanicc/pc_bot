# Telegram Remote Control PC Bot

A cross-platform Telegram bot for remote PC control. Currently only for Windows and Linux on systemd

made by ksanicc and using some ai for studying

please dont blame me im only studying its my first project

## Quick Start

### 1. **Downloading project**
Clone the repository
```bash
git clone https://github.com/ksanicc/pc_bot
cd pc_bot
```
Create and init `.venv`
```bash
python -m venv .venv    
source .venv/bin/activate    # Verify init with "which python", it should point to .venv/bin/python
```
for Windows (use `Set-ExecutionPolicy Unrestricted -Scope Process` if venv not works)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # Verify init with "Get-Command python", it should point to .venv\Scripts\python.exe
```

Install reqs and copy `.env`
```bash
python -m pip install -r requirements.txt

cp .env.example .env
```
Edit `.env`
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
WIN_ORDER=your_win_order
PROXY=your_proxy_or_None
SHELL=/usr/bin/your_shell
```

### 2. **Proxy setup**
Edit `PROXY` in `.env` if you need to change proxy or leave it empty
```env
PROXY=your_proxy
```

### 3. **Service**
To add this script in your service, just exec `add_service.py`
```bash
python add_service.py
```
### 4. **/win Command**
If you have DualBoot you can configure `/win` command to switch to Windows while on Linux without entering GRUB. 

**Need to mention it**, the `efibootmgr -n` is a one-time command, after rebooting your order will be as it was cause of `-n` flag. For someone it would be better, either not

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
Then you need to change `WIN_ORDER` in `.env` to your order
```env
WIN_ORDER=your_win_order
```
After that, you need to include `efibootmgr` and `systemctl` to `sudoers` (to prevent sudo requesting a passwords for changing bootorder), by using `echo` + `tee`
```bash
echo "$USER ALL=(ALL) NOPASSWD: /usr/bin/efibootmgr, /usr/bin/systemctl reboot" | sudo tee /etc/sudoers.d/pc_bot_nopass    # you can name "pc_bot_nopass" by whatever you want
```
Give it right permissions
```bash
sudo chmod 0440 /etc/sudoers.d/pc_bot_nopass    # you can check syntax by using "sudo visudo -c"
```
Now you can freely use `/win`

### 5. **/terminal Command**
This command is used to execute zsh/bash commands (Only for Linux now). To change shell edit `.env`
```env
SHELL=/usr/bin/your_shell
```
Supported flags:
```text
--no-log, -nolog    # disables stdout and stderr
--no-timeout, -notimeout    # disables timeout
--background, -bg    # makes procces background
```
Examples:
```bash
/terminal uptime
/terminal -nolog echo "password" | sudo -S dnf update -y
/terminal --no-timeout --no-log echo "password" | sudo -S dnf upgrade -y
/terminal -notimeout -bg steam
```
