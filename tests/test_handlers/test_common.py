from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext

from bot.common.handlers import cmd_start, CreateUser
from bot.common.keyboards import choose_role
from tests.conftest import TESTUSER


@pytest.mark.asyncio
async def test_start_cmd(redis_storage_fixture, storage_key_fixture, db_session_fixture):
    message = AsyncMock()
    message.from_user = TESTUSER
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    assert await state.get_state() is None

    async with db_session_fixture.begin() as session:
        # await delete_parent(session, TESTUSER.id)
        await cmd_start(message, session, state)

    assert await state.get_state() == CreateUser.ChooseRole

    message.answer.assert_called_with(
        'Привіт! Я бот для репетиторів, їх учнів та батьків. А ти хто?',
        reply_markup=choose_role
    )

@pytest.mark.asyncio
async def test_start_cmd_registered_user(redis_storage_fixture, storage_key_fixture, db_session_fixture):
    message = AsyncMock()
    message.from_user = TESTUSER
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    assert await state.get_state() is None

    async with db_session_fixture.begin() as session:
#         await delete_parent(session, TESTUSER.id)
#         await create_parent(session, TESTUSER.id, TESTUSER.username, 'Ім\'я', 'Прізвище')
        await cmd_start(message, session, state)
#         await delete_parent(session, TESTUSER.id)
    assert await state.get_state() is None

    message.answer.assert_called_with('Привіт! Я бот для репетиторів, їх учнів та батьків. Радий знову тебе бачити!')