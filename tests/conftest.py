import asyncio
import os

import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import User, Chat
from dotenv import load_dotenv
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.middlewares.db import DbSessionMiddleware
from tests.mocked_bot import MockedBot

TESTUSER = User(id=1, is_bot=False, first_name="FirstName1", last_name="LastName1", language_code="uk-UA",
                username="um")

TESTCHAT = Chat(id=1, type='private')


@pytest.fixture()
def bot():
    return MockedBot()


@pytest.fixture(name="storage_key_fixture")
def storage_key_fixture(bot: MockedBot):
    return StorageKey(chat_id=TESTCHAT.id, user_id=TESTUSER.id, bot_id=bot.id)


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def redis_storage_fixture(event_loop):
    redis_fixture = Redis(host='localhost', port=6379, db=3)
    storage = RedisStorage(redis=redis_fixture)
    try:
        await storage.redis.info()
        yield storage
    except ConnectionError as e:
        pytest.fail(str(e))
    finally:
        await redis_fixture.flushdb()
        await redis_fixture.aclose()


@pytest.fixture(scope="function")
def db_session_fixture():
    load_dotenv()
    engine = create_async_engine(url=os.getenv('TEST_DB_URL'), echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=True)
    return sessionmaker


@pytest_asyncio.fixture()
async def dispatcher(db_session_fixture):
    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=db_session_fixture))
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()
