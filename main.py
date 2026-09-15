import platform
import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession

def platform_system():
    return platform.system()

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
session = AiohttpSession(proxy="socks5://127.0.0.1:10808")
bot = Bot(token=bot_token, session=session)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    print(f"Получена команда /start от {message.from_user.id}")
    user_name = message.from_user.full_name if message.from_user else "Пользователь"
    await message.answer(f"Your name is: {user_name}\n\nActive sys: {platform_system()}")

async def main():
    print("Запуск поллинга бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
