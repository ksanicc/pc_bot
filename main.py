import platform
import os
import asyncio
import subprocess
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import BaseFilter
from aiogram import F, Router

session = None

#session = AiohttpSession(proxy="socks5://127.0.0.1:10808")

def platform_system():
    return platform.system()

load_dotenv(override=True)

help_cmd = {
    "/start": "Restart the bot",
    "/help": "Displays all commands",
    "/reboot": "Reboot PC",
    "/win": "Switch to Windows while on Linux",
}

bot_token = os.getenv("BOT_TOKEN")

admin_id = int(os.getenv("ADMIN_ID").strip())

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