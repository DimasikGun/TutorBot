from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot.common.handlers import cmd_start, CreateUser, create_user_add_name, create_user_add_surname, \
    create_user_add_phone, create_user_add_second_name, create_user_grade, create_user_discord, create_user_add_parent, \
    create_tutor_lesson_max_duration
from bot.common.keyboards import choose_role, choose_grade, skip_keyboard
from db.queries.common import delete_parent, create_parent, delete_tutor, delete_student
from tests.conftest import TESTUSER


@pytest.mark.asyncio
async def test_start_cmd(redis_storage_fixture, storage_key_fixture, db_session_fixture):
    message = AsyncMock()
    message.from_user = TESTUSER
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    assert await state.get_state() is None

    async with db_session_fixture.begin() as session:
        await delete_parent(session, TESTUSER.id)
    async with db_session_fixture.begin() as session:
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
        await delete_parent(session, TESTUSER.id)
    async with db_session_fixture.begin() as session:
        await create_parent(session, TESTUSER.id, TESTUSER.username, 'Ім\'я', 'Прізвище')
    async with db_session_fixture.begin() as session:
        await cmd_start(message, session, state)
    async with db_session_fixture.begin() as session:
        await delete_parent(session, TESTUSER.id)
    assert await state.get_state() is None

    message.answer.assert_called_with('Привіт! Я бот для репетиторів, їх учнів та батьків. Радий знову тебе бачити!')


@pytest.mark.asyncio
async def test_create_user_add_name_valid(redis_storage_fixture, storage_key_fixture):
    message = AsyncMock()
    message.text = 'Ім\'я'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    await create_user_add_name(message, state)

    assert await state.get_state() == CreateUser.Surname
    message.answer.assert_called_with('Введіть своє прізвище')


@pytest.mark.asyncio
async def test_create_user_add_name_invalid(redis_storage_fixture, storage_key_fixture):
    message = AsyncMock()
    message.text = '12345'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    await create_user_add_name(message, state)

    assert await state.get_state() == CreateUser.Name
    message.answer.assert_called_with('Введіть справжнє ім\'я')


@pytest.mark.asyncio
async def test_create_user_add_surname_valid(redis_storage_fixture, storage_key_fixture):
    message = AsyncMock()
    message.text = 'Прізвище'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    await create_user_add_surname(message, state)

    assert await state.get_state() == CreateUser.Phone
    message.answer.assert_called_with('Введіть свій номер телефону')


@pytest.mark.asyncio
async def test_create_user_add_surname_invalid(redis_storage_fixture, storage_key_fixture):
    message = AsyncMock()
    message.text = '12345'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    await create_user_add_surname(message, state)

    assert await state.get_state() == CreateUser.Surname
    message.answer.assert_called_with('Введіть справжнє прізвище')


@pytest.mark.asyncio
async def test_create_user_add_phone_valid(redis_storage_fixture, storage_key_fixture, db_session_fixture):
    message = AsyncMock()
    message.text = '+380123456789'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)
    await state.update_data(role='Учень')

    async with db_session_fixture.begin() as session:
        await create_user_add_phone(message, state, session)

    assert await state.get_state() == CreateUser.Grade
    message.answer.assert_called_with(
        'Введіть клас в якому ви навчаєтесь або натисніть кнопку "Я займаюсь без батьків", якщо ви дорослий і будете комунікувати із репетиторами власноруч',   # noqa E501
        reply_markup=choose_grade
    )


@pytest.mark.asyncio
async def test_create_user_add_phone_invalid(redis_storage_fixture, storage_key_fixture):
    message = AsyncMock()
    message.text = 'неверный номер'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    await create_user_add_phone(message, state, None)

    assert await state.get_state() == CreateUser.Phone
    message.answer.assert_called_with('Введіть справжній номер телефону')


@pytest.mark.asyncio
async def test_create_user_add_second_name_valid(redis_storage_fixture, storage_key_fixture):
    message = AsyncMock()
    message.text = 'По-батькові'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    await create_user_add_second_name(message, state)

    assert await state.get_state() == CreateUser.Discord
    message.answer.assert_called_with('Введіть свій нік Discord, або натисніть кнопку "Пропустити"',
                                      reply_markup=skip_keyboard)


@pytest.mark.asyncio
async def test_create_user_add_second_name_invalid(redis_storage_fixture, storage_key_fixture):
    message = AsyncMock()
    message.text = '12345'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    await create_user_add_second_name(message, state)

    assert await state.get_state() == CreateUser.SecondName
    message.answer.assert_called_with('Введіть справжнє по-батькові')


@pytest.mark.asyncio
async def test_create_user_grade_valid(redis_storage_fixture, storage_key_fixture):
    message = AsyncMock()
    message.text = '10'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    await create_user_grade(message, state)

    assert await state.get_state() == CreateUser.Discord
    message.answer.assert_called_with('Введіть свій нік Discord, або натисніть кнопку "Пропустити"',
                                      reply_markup=skip_keyboard)


@pytest.mark.asyncio
async def test_create_user_grade_invalid(redis_storage_fixture, storage_key_fixture):
    message = AsyncMock()
    message.text = 'Класс неверный'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    await create_user_grade(message, state)

    assert await state.get_state() == CreateUser.Grade
    message.answer.assert_called_with('Введіть коректну інформацію')


@pytest.mark.asyncio
async def test_create_user_discord_valid(redis_storage_fixture, storage_key_fixture, db_session_fixture):
    message = AsyncMock()
    message.text = 'Пропустити'
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    # Заполнение всех необходимых данных в state
    await state.update_data(
        role='Учень',
        name='Иван',
        surname='Иванов',
        phone='+380123456789',
        grade=10
    )

    async with db_session_fixture.begin() as session:
        await create_user_discord(message, state, session)

    assert await state.get_state() == CreateUser.Parent
    message.answer.assert_called_with('Введіть код, який вам надав один із батьків для створення "Сім\'ї"',
                                      reply_markup=ReplyKeyboardRemove())


@pytest.mark.asyncio
async def test_create_user_discord_invalid(redis_storage_fixture, storage_key_fixture, db_session_fixture):
    message = AsyncMock()
    message.from_user = TESTUSER
    message.text = 'неверный ник'
    message.from_user = TESTUSER
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    async with db_session_fixture.begin() as session:
        await create_user_discord(message, state, session)

    assert await state.get_state() == CreateUser.Discord
    message.answer.assert_called_with('Введіть коректну інформацію')


@pytest.mark.asyncio
async def test_create_user_add_parent_valid(redis_storage_fixture, storage_key_fixture, db_session_fixture):
    message = AsyncMock()
    message.text = 2
    message.from_user = TESTUSER
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    async with db_session_fixture.begin() as session:
        await create_parent(session, 2, TESTUSER.username, 'Ім\'я', 'Прізвище')
    # Заполнение всех необходимых данных в state
    await state.update_data(
        role='Учень',
        name='Иван',
        surname='Иванов',
        phone='+380123456789',
        grade=10,
        discord=None
    )

    async with db_session_fixture.begin() as session:
        await create_user_add_parent(message, state, session)
    async with db_session_fixture.begin() as session:
        await delete_student(session, TESTUSER.id)
    async with db_session_fixture.begin() as session:
        await delete_parent(session, 2)

    assert await state.get_state() is None
    message.answer.assert_called_with('Дякуємо за реєстрацію!', reply_markup=ReplyKeyboardRemove())


@pytest.mark.asyncio
async def test_create_user_add_parent_invalid(redis_storage_fixture, storage_key_fixture):
    message = AsyncMock()
    message.text = 'неверный код'
    message.from_user = TESTUSER
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    # Заполнение всех необходимых данных в state
    await state.update_data(
        role='Учень',
        name='Иван',
        surname='Иванов',
        phone='+380123456789',
        grade='10'
    )

    await create_user_add_parent(message, state, None)

    assert await state.get_state() == CreateUser.Parent
    message.answer.assert_called_with('Введіть коректний код одного з батьків')


@pytest.mark.asyncio
async def test_create_tutor_lesson_max_duration_valid(redis_storage_fixture, storage_key_fixture, db_session_fixture):
    message = AsyncMock()
    message.text = '3'
    message.from_user = TESTUSER
    state = FSMContext(storage=redis_storage_fixture, key=storage_key_fixture)

    # Заполнение всех необходимых данных в state
    await state.update_data(
        role='Репетитор',
        name='Иван',
        surname='Иванов',
        second_name='Иванов',
        discord=None,
        phone='+380123456789',
        lesson_max_duration=3
    )

    async with db_session_fixture.begin() as session:
        await create_tutor_lesson_max_duration(message, state, session)
    async with db_session_fixture.begin() as session:
        await delete_tutor(session, TESTUSER.id)

    assert await state.get_state() is None
    message.answer.assert_called_with('Дякуємо за реєстрацію!', reply_markup=ReplyKeyboardRemove())
