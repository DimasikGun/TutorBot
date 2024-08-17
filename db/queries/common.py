from sqlalchemy.ext.asyncio import AsyncSession
from db import Tutors, Parents, Students
from db.queries.services import get_single_object_by_id, create_db_item, cache_db_item


async def get_single_parent(session: AsyncSession, user_id):
    """Fetches a single parent object by user_id."""
    parent = await get_single_object_by_id(session, user_id, f'parent:{user_id}', Parents)
    return parent


async def get_single_student(session: AsyncSession, user_id):
    """Fetches a single student object by user_id."""
    student = await get_single_object_by_id(session, user_id, f'student:{user_id}', Students)
    return student


async def get_single_tutor(session: AsyncSession, user_id):
    """Fetches a single tutor object by user_id."""
    tutor = await get_single_object_by_id(session, user_id, f'tutor:{user_id}', Tutors)
    return tutor


async def get_single_user(session: AsyncSession, user_id):
    """Fetches a single user object, searching in parents, students, and tutors."""
    parent = await get_single_parent(session, user_id)
    student = await get_single_student(session, user_id)
    tutor = await get_single_tutor(session, user_id)
    return parent or student or tutor


async def create_tutor(session: AsyncSession, user_id, username, name, surname, phone, second_name,
                       lesson_max_duration, discord):
    """Creates a new tutor record in the database and caches it."""
    tutor = Tutors(user_id=user_id, username=username, name=name, surname=surname, phone=phone, second_name=second_name,
                   lesson_max_duration=lesson_max_duration, discord=discord)
    await create_db_item(session, tutor)
    await cache_db_item(tutor, f'tutor:{user_id}')
    return tutor


async def create_student(session: AsyncSession, user_id, username, name, surname, phone, parent, discord, grade):
    """Creates a new student record in the database and caches it."""
    student = Students(user_id=user_id, username=username, name=name, surname=surname, phone=phone,
                       parent=parent, discord=discord, grade=grade)
    await create_db_item(session, student)
    await cache_db_item(student, f'student:{user_id}')
    return student


async def create_parent(session: AsyncSession, user_id, username, name, surname, phone):
    """Creates a new parent record in the database and caches it."""
    parent = Parents(user_id=user_id, username=username, name=name, surname=surname, phone=phone)
    await create_db_item(session, parent)
    await cache_db_item(parent, f'parent:{user_id}')
    return parent
