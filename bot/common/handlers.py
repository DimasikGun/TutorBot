from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bot.common.keyboards import choose_role, choose_grade, skip_keyboard
from bot.common.services import validate_ukrainian_letters, validate_phone_number, validate_discord_username
from db.queries.common import get_single_user, create_student, create_parent, create_tutor

router = Router()


class CreateUser(StatesGroup):
    ChooseRole = State()
    Name = State()
    Surname = State()
    Phone = State()
    Grade = State()
    SecondName = State()
    Discord = State()
    LessonMaxDuration = State()
    Parent = State()


@router.message(Command('start'))
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext):
    """Handles the '/start' command and welcomes the user."""
    user = await get_single_user(session, message.from_user.id)
    if not user:
        await state.set_state(CreateUser.ChooseRole)
        await state.update_data(user_id=message.from_user.id, username=message.from_user.username)
        await message.answer('Привіт! Я бот для репетиторів, їх учнів та батьків. А ти хто?', reply_markup=choose_role)
    else:
        await message.answer('Привіт! Я бот для репетиторів, їх учнів та батьків. Радий знову тебе бачити!')


@router.message(CreateUser.ChooseRole)
async def start_create_user(message: Message, state: FSMContext):
    """Start creating user"""
    if message.text in ('Репетитор', 'Учень', 'Батько/Мати'):
        await state.set_state(CreateUser.Name)
        await state.update_data(role=message.text)
        await message.answer('Введіть своє ім\'я', reply_markup=ReplyKeyboardRemove())
    else:
        await state.set_state(CreateUser.ChooseRole)
        await message.answer('Оберіть один із варіантів')


@router.message(CreateUser.Name)
async def create_user_add_name(message: Message, state: FSMContext):
    """Saves name of user"""
    if validate_ukrainian_letters(message.text):
        await state.update_data(name=message.text)
        await state.set_state(CreateUser.Surname)
        await message.answer('Введіть своє прізвище')
    else:
        await state.set_state(CreateUser.Name)
        await message.answer('Введіть справжнє ім\'я')


@router.message(CreateUser.Surname)
async def create_user_add_surname(message: Message, state: FSMContext):
    """Saves surname of user"""
    if validate_ukrainian_letters(message.text):
        await state.update_data(surname=message.text)
        await state.set_state(CreateUser.Phone)
        await message.answer('Введіть свій номер телефону')
    else:
        await state.set_state(CreateUser.Surname)
        await message.answer('Введіть справжнє прізвище')


@router.message(CreateUser.Phone)
async def create_user_add_phone(message: Message, state: FSMContext, session: AsyncSession):
    """Saves phone number of user"""
    if validate_phone_number(message.text):
        data = await state.get_data()
        if data['role'] == 'Батько/Мати':
            await create_parent(session, message.from_user.id, message.from_user.username, data['name'],
                                data['surname'], message.text)
            await message.answer('Дякуємо за реєстрацію!',
                                 reply_markup=ReplyKeyboardRemove())
            await state.clear()
        elif data['role'] == 'Учень':
            await state.update_data(phone=message.text)
            await state.set_state(CreateUser.Grade)
            await message.answer(
                'Введіть клас в якому ви навчаєтесь або натисніть кнопку "Я займаюсь без батьків", якщо ви дорослий і будете комунікувати із репетиторами власноруч',  # noqa: E501
                reply_markup=choose_grade)
        else:
            await state.update_data(phone=message.text)
            await state.set_state(CreateUser.SecondName)
            await message.answer(
                'Введіть ваше по-батькові',
                reply_markup=skip_keyboard)
    else:
        await state.set_state(CreateUser.Phone)
        await message.answer('Введіть справжній номер телефону')


@router.message(CreateUser.SecondName)
async def create_user_add_second_name(message: Message, state: FSMContext):
    """Saves second_name of tutor"""
    if validate_ukrainian_letters(message.text):
        await state.update_data(second_name=message.text)
        await state.set_state(CreateUser.Discord)
        await message.answer('Введіть свій нік Discord, або натисніть кнопку "Пропустити"', reply_markup=skip_keyboard)
    else:
        await state.set_state(CreateUser.SecondName)
        await message.answer('Введіть справжнє по-батькові')


@router.message(CreateUser.Grade)
async def create_user_grade(message: Message, state: FSMContext):
    """Saves grade of student"""
    if message.text == 'Я займаюсь без батьків':
        await state.update_data(grade=None)
        await state.set_state(CreateUser.Discord)
        await message.answer('Введіть свій нік Discord, або натисніть кнопку "Пропустити"', reply_markup=skip_keyboard)
    else:
        try:
            if 1 <= int(message.text) <= 12:
                await state.update_data(grade=int(message.text))
                await state.set_state(CreateUser.Discord)
                await message.answer('Введіть свій нік Discord, або натисніть кнопку "Пропустити"',
                                     reply_markup=skip_keyboard)
            else:
                await state.set_state(CreateUser.Grade)
                await message.answer('Введіть коректну інформацію')
        except:
            await state.set_state(CreateUser.Grade)
            await message.answer('Введіть коректну інформацію')


@router.message(CreateUser.Discord)
async def create_user_discord(message: Message, state: FSMContext, session: AsyncSession):
    """Saves discord of user"""
    data = await state.get_data()
    if message.text == 'Пропустити':
        await state.update_data(discord=None)
        if data.get('grade', None):
            await state.set_state(CreateUser.Parent)
            await message.answer('Введіть код, який вам надав один із батьків для створення "Сім\'ї"',
                                 reply_markup=ReplyKeyboardRemove())
        elif data['role'] == 'Репетитор':
            await state.set_state(CreateUser.LessonMaxDuration)
            await message.answer('Введіть максимальну тривалість вашого уроку. Цей параметр можна змінити пізніше',
                                 reply_markup=ReplyKeyboardRemove())
        else:
            await create_student(session, message.from_user.id, message.from_user.username, data['name'],
                                 data['surname'], data['phone'], balance=0)
            await message.answer('Дякуємо за реєстрацію!',
                                 reply_markup=ReplyKeyboardRemove())
            await state.clear()
    elif validate_discord_username(message.text):
        if data.get('grade', None):
            await state.update_data(discord=message.text)
            await state.set_state(CreateUser.Parent)
            await message.answer('Введіть код, який вам надав один із батьків для створення "Сім\'ї"',
                                 reply_markup=ReplyKeyboardRemove())
        elif data['role'] == 'Репетитор':
            await state.update_data(discord=message.text)
            await state.set_state(CreateUser.LessonMaxDuration)
            await message.answer('Введіть максимальну тривалість вашого уроку. Цей параметр можна змінити пізніше',
                                 reply_markup=ReplyKeyboardRemove())
        else:
            await create_student(session, message.from_user.id, message.from_user.username, data['name'],
                                 data['surname'], data['phone'], discord=message.text, balance=0)
            await message.answer('Дякуємо за реєстрацію!',
                                 reply_markup=ReplyKeyboardRemove())
            await state.clear()
    else:
        await state.set_state(CreateUser.Discord)
        await message.answer('Введіть коректну інформацію')


@router.message(CreateUser.Parent)
async def create_user_add_parent(message: Message, state: FSMContext, session: AsyncSession):
    """Saves parent of student"""
    data = await state.get_data()
    try:
        await create_student(session, message.from_user.id, message.from_user.username, data['name'],
                             data['surname'], data['phone'], int(message.text), data['discord'], data['grade'])
        await message.answer('Дякуємо за реєстрацію!',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()
    except (IntegrityError, ValueError):
        await state.set_state(CreateUser.Parent)
        await message.answer('Введіть коректний код одного з батьків')


@router.message(CreateUser.LessonMaxDuration)
async def create_tutor_lesson_max_duration(message: Message, state: FSMContext, session: AsyncSession):
    """Saves lesson maximum duration of tutor"""
    try:
        if 1 <= int(message.text) <= 6:
            data = await state.get_data()
            await create_tutor(session, message.from_user.id, message.from_user.username, data['name'],
                               data['surname'], data['phone'], data['second_name'], int(message.text), data['discord'])
            await message.answer('Дякуємо за реєстрацію!',
                                 reply_markup=ReplyKeyboardRemove())
            await state.clear()
        else:
            await state.set_state(CreateUser.LessonMaxDuration)
            await message.answer('Введіть коректну інформацію')
    except ValueError:
        await state.set_state(CreateUser.LessonMaxDuration)
        await message.answer('Введіть коректну інформацію')
