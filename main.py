import platform
import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import BaseFilter
from aiogram import F, Router

def platform_system():
    return platform.system()

load_dotenv(override=True)

bot_token = os.getenv("BOT_TOKEN")

admin_id = int(os.getenv("ADMIN_ID").strip())

session = AiohttpSession(proxy="socks5://127.0.0.1:10808")

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
    await message.answer(f"User: {message.from_user.full_name}\nActive sys: {platform_system()}")

# USER SECTION

user_router = Router()

@user_router.message(CommandStart())
async def start_handler(message: Message):
    print(f"[USER] Команда /start от {message.from_user.id}")
    user_name = message.from_user.full_name if message.from_user else "Пользователь"
    await message.answer(f"Your name is: {user_name}")

dp.include_routers(admin_router, user_router)

async def main():
    
    print("Запуск поллинга бота...")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 