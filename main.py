import asyncio
from aiogram import Bot, Dispatcher
from bot.handlers import router
from database.models import async_main
from config import config
import logging


async def main():
    logging.basicConfig(level=logging.INFO)
    await async_main()
    bot = Bot(token=config["telegram_bot_token"])
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())