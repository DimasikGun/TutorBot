from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext

from bot.common.handlers import cmd_start, CreateUser
from bot.common.keyboards import choose_role
from bot.tests.conftest import TESTUSER


@pytest.mark.asyncio
async def test_start_cmd(redis_storage_fixture, storage_key_fixture, db_session_fixture):
    message = AsyncMock()
    message.from_user = TESTUSER
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    assert await state.get_state() is None

    async with db_session_fixture.begin() as session:
        await cmd_start(message, session, state)

    assert await state.get_state() == CreateUser.ChooseRole

    message.answer.assert_called_with(
        'Привіт! Я бот для репетиторів, їх учнів та батьків. А ти хто?',
        reply_markup=choose_role
    )

