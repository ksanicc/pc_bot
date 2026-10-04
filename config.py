import os
import platform
from dotenv import load_dotenv


load_dotenv(override=True)


BOT_TOKEN = os.getenv("BOT_TOKEN")
RAW_ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_ID = int(RAW_ADMIN_ID.strip()) if RAW_ADMIN_ID else 0

SHELL = os.getenv("SHELL")
PROXY = os.getenv("PROXY")
WIN_ORDER = os.getenv("WIN_ORDER")

def get_platform():
    return platform.system()

help_cmd = {
    "/start": "Restart the bot",
    "/help": "Displays all commands",
    "/reboot": "Reboot PC",
    "/win": "Switch to Windows while on Linux",
    "/terminal": "Use Linux terminal",
    "/status": "Shows CPU usage, RAM usage, Disks usage on Linux"
}