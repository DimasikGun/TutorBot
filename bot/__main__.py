import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from bot.common.handlers import router
from bot.middlewares.db import DbSessionMiddleware

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))


async def main():
    engine = create_async_engine(url=os.getenv('DB-URL'), echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=True)
    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.include_routers(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('end of work')
