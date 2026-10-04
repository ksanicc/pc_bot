from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from config import ADMIN_ID, WIN_ORDER, SHELL, get_platform, help_cmd
import asyncio
import os
import re

admin_router = Router()

admin_router.message.filter(F.from_user.id == ADMIN_ID)

@admin_router.message(CommandStart())
async def admin_start(message: Message):
    await message.answer(f"Hi {message.from_user.full_name}\nActive system: {get_platform()}")
    
@admin_router.message(Command("reboot"))
async def admin_reboot(message: Message):
    if get_platform() == "Linux":
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
    
    if get_platform() != "Linux":
        await message.answer("Command /win is only available on Linux")
        return
    
    if not WIN_ORDER:
        await message.answer("WIN_ORDER not found in .env")
        return
    
    await message.answer("Switching to Windows")
    await asyncio.sleep(1)
    
    efiboot = await asyncio.create_subprocess_exec("sudo", "-n", "/usr/bin/efibootmgr", "-n", WIN_ORDER)
    
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
    
    is_win = get_platform() == "Windows"
    
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
                f"/run/user/{uid}/gdm/Xauthority"
            ]
            
            run_user_dir = f"/run/user/{uid}"
            if os.path.exists(run_user_dir):
                for fname in os.listdir(run_user_dir):
                    if fname.startswith("xauth_"):
                        possible_xauth.append(os.path.join(run_user_dir, fname))
            
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
                    executable=SHELL,
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
                executable=SHELL,
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
        executable=SHELL
    )
    
    stdout, stderr = await process.communicate()
    
    out = stdout.decode("utf-8", errors="replace").strip()
    
    await message.reply(f"```\n{out}\n```", parse_mode="Markdown")