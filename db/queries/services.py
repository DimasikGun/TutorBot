import json
from datetime import datetime

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# initialize it in this file due to circular import issue
redis = Redis(host='localhost', port=6379, db=1)


async def get_single_db_item(session: AsyncSession, stmt):
    """Executes and scalars single db object"""
    result = await session.execute(stmt)
    obj = result.scalar()
    return obj


async def get_many_db_items(session: AsyncSession, stmt):
    """Executes and scalars list of db objects"""
    result = await session.execute(stmt)
    obj = result.scalars().all()
    return obj


async def create_db_item(session: AsyncSession, stmt):
    """Add object to session and commit it"""
    session.add(stmt)
    await session.commit()


async def serialize_single_db_item(obj):
    """Serializes single SQLAlchemy object into JSON format"""
    serialized_single_data = {}
    for key, value in obj.__dict__.items():
        if key not in ['metadata', 'registry', '_sa_instance_state']:
            if isinstance(value, datetime):
                serialized_single_data[key] = value.isoformat()
            else:
                serialized_single_data[key] = value
    serialized_data_json = json.dumps(serialized_single_data)
    return serialized_data_json


async def serialize_many_db_items(obj):
    """Serializes list of SQLAlchemy objects into JSON format"""
    serialized_data = []
    for item in obj:
        serialized_single_data = await serialize_single_db_item(item)
        serialized_data.append(serialized_single_data)

    serialized_data_json = json.dumps(serialized_data)
    return serialized_data_json


async def deserialize_single_db_item(obj):
    """Deserializes JSON object into single SQLAlchemy object"""
    date_attributes = ["reg_date", "upd_date", "add_date", "finish_date"]

    for attr in date_attributes:
        if attr in obj and obj[attr] is not None:
            obj[attr] = datetime.fromisoformat(obj[attr])

    return obj


async def deserialize_db_items(json_obj):
    """Deserializes JSON object into list of SQLAlchemy objects or into a single one"""
    deserialized_data = json.loads(json_obj)

    if isinstance(deserialized_data, list):
        for item in deserialized_data:
            await deserialize_single_db_item(item)
    else:
        await deserialize_single_db_item(deserialized_data)
    return deserialized_data


async def get_cached_db_item(redis_key):
    """Gets JSON object from redis and deserializes it into db object"""
    cached_item = await redis.get(redis_key)
    obj_attributes = None
    if cached_item:
        obj_attributes = await deserialize_db_items(cached_item)
    return obj_attributes


async def cache_db_item(obj, redis_key):
    """Sets JSON object to redis"""
    if isinstance(obj, list):
        serialized_obj = await serialize_many_db_items(obj)
    else:
        serialized_obj = await serialize_single_db_item(obj)
    await redis.set(redis_key, serialized_obj)
    await redis.expire(redis_key, 604800)


async def get_single_object_by_id(session: AsyncSession, object_id, redis_key, model):
    """Template function for getting single object by id"""
    obj_attrs = await get_cached_db_item(redis_key)
    if obj_attrs:
        obj = model(**obj_attrs)
    else:
        stmt = select(model).where(model.user_id == object_id)
        obj = await get_single_db_item(session, stmt)
        if obj:
            await cache_db_item(obj, redis_key)
    return obj
