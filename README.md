# Telegram Remote Control PC Bot

A cross-platform Telegram bot for remote PC administration.

made by ksanicc and using some ai for studying

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

To change proxy: Edit line 25 in main.py with your custom proxy URL.

To disable proxy: Comment out line 25 in main.py.

### 3. **Service**
To add this script in your service, just exec add_service.py
```bash
python add_service.py
```