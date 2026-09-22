import platform
import os
import asyncio
import subprocess
import re
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import BaseFilter
from aiogram import F, Router
from aiogram import types

def platform_system():
    return platform.system()

load_dotenv(override=True)

help_cmd = {
    "/start": "Restart the bot",
    "/help": "Displays all commands",
    "/reboot": "Reboot PC",
    "/win": "Switch to Windows while on Linux",
    "/terminal": "Use Linux terminal",
    "/status": "Shows CPU usage, RAM usage, Disks usage on Linux"
}

bot_token = os.getenv("BOT_TOKEN")

admin_id = int(os.getenv("ADMIN_ID").strip())

shell = os.getenv("SHELL")

proxy = os.getenv("PROXY")

session = AiohttpSession(proxy=f"{proxy}")

bot = Bot(token=bot_token, session=session)

dp = Dispatcher()

# ADMIN SECTION

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.from_user and message.from_user.id == admin_id)

admin_router = Router() 
    
admin_router.message.filter(F.from_user.id == admin_id)


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    await message.answer(f"Hi {message.from_user.full_name}\nActive system: {platform_system()}")
    
@admin_router.message(Command("reboot"))
async def admin_reboot(message: Message):
    if platform_system() == "Linux":
        await message.answer("Rebooting Linux")
        await asyncio.sleep(1)
        await asyncio.create_subprocess_exec("sudo", "-n", "/usr/bin/systemctl", "reboot")
    else:
        await message.answer("Rebooting Windows")
        await asyncio.sleep(1)
        await asyncio.create_subprocess_exec("shutdown", "/r", "/t", "0")
        
@admin_router.message(Command("help"))
async def admin_help(message: Message):
    text_lines = [f"{cmd} — {desc}" for cmd, desc in help_cmd.items()]
    full_text = "\n".join(text_lines)
    await message.answer(full_text)

@admin_router.message(Command("win"))
async def admin_win(message: Message):
    
    win_order = os.getenv("WIN_ORDER")
    
    if platform_system() != "Linux":
        await message.answer("Command /win is only available on Linux")
        return
    
    if not win_order:
        await message.answer("WIN_ORDER not found in .env")
        return
    
    await message.answer("Switching to Windows")
    await asyncio.sleep(1)
    
    efiboot = await asyncio.create_subprocess_exec("sudo", "-n", "/usr/bin/efibootmgr", "-n", win_order)
    
    efiboot_check = await efiboot.wait()

    if efiboot_check == 0:
        await asyncio.create_subprocess_exec("sudo", "-n", "/usr/bin/systemctl", "reboot")
    else:
        await message.answer("Error. smth with efiboot")
        return

@admin_router.message(Command("terminal"))
async def admin_terminal(message: Message):
    
    command_text = message.text.split(maxsplit=1)
    
    if len(command_text) < 2:
        await message.reply("Please enter the command")
        return

    term_args = command_text[1] 
    
    no_log = bool(re.search(r'(?i)(?:^|\s)(?:-nolog|--no-log)(?:\s|$)', term_args))
    no_timeout = bool(re.search(r'(?i)(?:^|\s)(?:-notimeout|--no-timeout)(?:\s|$)', term_args))
    bg = bool(re.search(r'(?i)(?:^|\s)(?:-bg|--background)(?:\s|$)', term_args))
    
    # await message.reply(f"no_log: {no_log}, no_timeout: {no_timeout}, bg: {bg}")
    
    cmd = re.sub(r'(?i)(?:--no-log|-nolog|--no-timeout|-notimeout|--background|-bg)', '', term_args)
    cmd = " ".join(cmd.split()).strip()
    
    timeout_val = None if no_timeout else 6.0
    
    is_win = platform_system() == "Windows"
    
    env = os.environ.copy()
    
    if not is_win:
        uid = os.getuid()

        if "DISPLAY" not in env or not env["DISPLAY"]:
            env["DISPLAY"] = ":0"
            
        if "XDG_RUNTIME_DIR" not in env:
            env["XDG_RUNTIME_DIR"] = f"/run/user/{uid}"
            
        if "WAYLAND_DISPLAY" not in env:
            env["WAYLAND_DISPLAY"] = "wayland-0"

        if "DBUS_SESSION_BUS_ADDRESS" not in env:
            env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{uid}/bus"
            
        if "XAUTHORITY" not in env:
            home = os.path.expanduser("~")
            possible_xauth = [
                os.path.join(home, ".Xauthority"),
                f"/run/user/{uid}/gdm/Xauthority",
                f"/tmp/xauth_{uid}"
            ]
            for path in possible_xauth:
                if os.path.exists(path):
                    env["XAUTHORITY"] = path
                    break
        
    if not cmd:
        await message.reply("Please enter the command")
        return
    
    if bg:
        try:
            if is_win:
                bg_cmd = f'start "" {cmd}'
                await asyncio.create_subprocess_shell(bg_cmd, env=env)
            else:
                await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                    stdin=asyncio.subprocess.DEVNULL,
                    executable=shell,
                    env=env
                )
            
            if not no_log:
                await message.reply(f"Started in background:\n`{cmd}`", parse_mode="Markdown")
            return
        except Exception as e:
            await message.reply(f"Background launch error:\n`{e}`", parse_mode="Markdown")
            return
    
    try:
        if is_win:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
        else:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                executable=shell,
                env=env
            )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_val)
            
        except asyncio.TimeoutError:
            process.kill()
            await message.reply("TimeoutError(600 seconds passed - command not ended)")
            return
        
        if no_log:
            code = process.returncode
            status_icon = "Done" if code == 0 else "Error"
            await message.reply(f"{status_icon}. (exit code: `{code}`).", parse_mode="Markdown")
            return
        
        encoding = "cp866" if is_win else "utf-8"
        
        out = stdout.decode(encoding, errors='replace').strip()
        
        err = stderr.decode(encoding, errors='replace').strip()
        
        full_output = f"=== STDOUT ===\n{out}\n\n=== STDERR ===\n{err}"
        
        if len(full_output) > 3500:
            if out:
                out = out[-3000:]
            if err:
                err = err[-3000:]
        response = ""
        if out:
            response += f"**STDOUT:**\n```bash\n{out}\n```\n"
        if err:
            response += f"**STDERR:**\n```bash\n{err}\n```\n"
        if not response:
            response = "Done"
        await message.reply(response, parse_mode="Markdown")
        
    except Exception as e:
        await message.reply(f"Error:\n`{e}`", parse_mode="Markdown")
        
@admin_router.message(Command("status"))
async def admin_status(message: Message):
    cmd = """echo "CPU Load:\n" && top -bn1 | grep "Cpu(s)" && echo -e "\nRAM:\n" && free -h && echo -e "\nDISKS:\n" && df -h -t ext4 -t btrfs -t xfs"""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        executable=shell
    )
    
    stdout, stderr = await process.communicate()
    
    out = stdout.decode("utf-8", errors="replace").strip()
    
    await message.reply(f"```\n{out}\n```", parse_mode="Markdown")
    
    
# USER SECTION

user_router = Router()

@user_router.message(CommandStart())
async def start_handler(message: Message):
    user_name = message.from_user.full_name if message.from_user else "Пользователь"
    await message.answer(f"You are not admin")

dp.include_routers(admin_router, user_router)

async def main():
    
    print("Turning polling")
    try:
        await bot.send_message(
            chat_id=admin_id, 
            text=f"PC turned on\nSystem: {platform_system()}", 
        )
    except Exception as e:
        print(f"Couldnt send message: {e}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 