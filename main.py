import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from config import BOT_TOKEN, PROXY, ADMIN_ID, get_platform
from handlers.admin import admin_router
from handlers.user import user_router

async def main():
    session = AiohttpSession(proxy=PROXY) if PROXY else None
    bot = Bot(token=BOT_TOKEN, session=session)
    
    dp = Dispatcher()
    dp.include_routers(admin_router, user_router)

    print("Turning polling...")
    try:
        await bot.send_message(
            chat_id=ADMIN_ID, 
            text=f"PC turned on\nSystem: {get_platform()}", 
        )
    except Exception as e:
        print(f"Could not send start message: {e}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())