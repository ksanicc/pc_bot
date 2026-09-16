import subprocess
import platform
import getpass
from pathlib import Path


username = getpass.getuser() 

sys_name = platform.system().lower()

# Получаем абсолютный путь к папке скрипта
script_dir = Path(__file__).resolve().parent


def linux():
    user_systemd_dir = Path.home() / ".config" / "systemd" / "user"
    service_file = user_systemd_dir / "pc_bot.service"

    service_content = f"""
[Unit]
Description=Telegram Remote Control PC Bot
After=network.target

[Service]
Type=simple
WorkingDirectory={script_dir}
ExecStart={script_dir}/.venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
    """
    
    user_systemd_dir.mkdir(parents=True, exist_ok=True)

    service_file.write_text(service_content, encoding="utf-8")
    print(f"File created: {service_file}")

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", "pc_bot.service"], check=True)
    subprocess.run(["loginctl", "enable-linger", username])
    print("Service pc_bot successfully created via systemd --user")


def win():
    python_exe = script_dir / ".venv" / "Scripts" / "python.exe"
    main_py = script_dir / "main.py"
    
    subprocess.run([
        "schtasks", "/Create",
        "/TN", "pc_bot",
        "/TR", f'"{python_exe}" "{main_py}"',
        "/SC", "ONLOGON",
        "/F"
    ], check=True)
    
    print("Task pc_bot successfully added to Windows")


def main():
    
    # Создаем словарь функций под каждую ОС
    actions = {
        "linux": linux,
        "windows": win
    }
    
    if sys_name in actions: 
        actions[sys_name]() # Вызываем нужную функцию
    else:
        print(f"Неподдерживаемая ОС: {sys_name}")

if __name__ == "__main__":
    main()