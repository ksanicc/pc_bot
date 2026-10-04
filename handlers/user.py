from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

user_router = Router()

@user_router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("You are not admin")