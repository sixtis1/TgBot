import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.handlers import router

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token="7062383295:AAGFO8oU4ZDenOTCXQHvGs-JSzzO_81-4o0")
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())