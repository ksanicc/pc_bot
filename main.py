import platform
import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

def platform_system():
    return platform.system()

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")

bot = Bot(token=bot_token)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_name = message.from_user.full_name if message.from_user else "Пользователь"
    await message.answer(f"Your name is: {user_name}\n\nActive sys: {platform_system()}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())