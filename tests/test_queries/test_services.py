import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import Users, Parents
from db.queries.services import serialize_single_db_item, serialize_many_db_items, deserialize_single_db_item, \
    deserialize_db_items, get_cached_db_item, cache_db_item, delete_single_object_by_id, get_single_object_by_id
from db.users import Notes


@pytest.mark.asyncio
async def test_serialize_single_db_item():
    obj = MagicMock()
    obj.__dict__ = {
        "id": 1,
        "name": "Test",
        "created_at": datetime(2023, 8, 23),
        "_sa_instance_state": "state"
    }

    result = await serialize_single_db_item(obj)
    expected_result = json.dumps({
        "id": 1,
        "name": "Test",
        "created_at": "2023-08-23T00:00:00"
    })
    assert result == expected_result


@pytest.mark.asyncio
async def test_serialize_many_db_items():
    obj1 = MagicMock()
    obj1.__dict__ = {"id": 1, "name": "Test1"}
    obj2 = MagicMock()
    obj2.__dict__ = {"id": 2, "name": "Test2"}

    result = await serialize_many_db_items([obj1, obj2])
    expected_result = json.dumps([
        json.dumps({"id": 1, "name": "Test1"}),
        json.dumps({"id": 2, "name": "Test2"})
    ])
    assert result == expected_result


@pytest.mark.asyncio
async def test_deserialize_single_db_item():
    obj = {"id": 1, "reg_date": "2023-08-23T00:00:00"}
    result = await deserialize_single_db_item(obj)
    assert isinstance(result['reg_date'], datetime)
    assert result['reg_date'] == datetime(2023, 8, 23, 0, 0, 0)


@pytest.mark.asyncio
async def test_deserialize_db_items_single():
    json_obj = json.dumps({"id": 1, "reg_date": "2023-08-23T00:00:00"})
    result = await deserialize_db_items(json_obj)
    assert isinstance(result['reg_date'], datetime)
    assert result['reg_date'] == datetime(2023, 8, 23, 0, 0, 0)


@pytest.mark.asyncio
async def test_deserialize_db_items_many():
    json_obj = json.dumps([
        {"id": 1, "reg_date": "2023-08-23T00:00:00"},
        {"id": 2, "upd_date": "2024-01-01T12:00:00"}
    ])
    result = await deserialize_db_items(json_obj)
    assert isinstance(result[0]['reg_date'], datetime)
    assert isinstance(result[1]['upd_date'], datetime)
    assert result[0]['reg_date'] == datetime(2023, 8, 23, 0, 0, 0)
    assert result[1]['upd_date'] == datetime(2024, 1, 1, 12, 0, 0)


@pytest.mark.asyncio
@patch('db.queries.services.redis.get', new_callable=AsyncMock)
async def test_get_cached_db_item(mock_redis_get):
    cached_data = json.dumps({"id": 1, "reg_date": "2023-08-23T00:00:00"})
    mock_redis_get.return_value = cached_data
    result = await get_cached_db_item('test_key')
    assert isinstance(result['reg_date'], datetime)
    assert result['reg_date'] == datetime(2023, 8, 23, 0, 0, 0)


@pytest.mark.asyncio
@patch('db.queries.services.redis.set', new_callable=AsyncMock)
@patch('db.queries.services.redis.expire', new_callable=AsyncMock)
async def test_cache_db_item(mock_redis_expire, mock_redis_set):
    obj = MagicMock()
    obj.__dict__ = {"id": 1, "name": "Test1"}
    await cache_db_item(obj, 'test_key')

    mock_redis_set.assert_called_once()
    mock_redis_expire.assert_called_once_with('test_key', 604800)


@pytest.mark.asyncio
@patch('db.queries.services.redis.delete', new_callable=AsyncMock)
@patch('db.queries.services.AsyncSession.execute', new_callable=AsyncMock)
@patch('db.queries.services.AsyncSession.commit', new_callable=AsyncMock)  # Мок для commit
async def test_delete_single_object_by_id(mock_commit, mock_execute, mock_redis_delete, db_session_fixture):
    object_id = 1
    redis_key = 'test_key'

    # Case 1: Non-Users model
    async with db_session_fixture() as session:
        await delete_single_object_by_id(session, object_id, redis_key, Notes)

        mock_execute.assert_called_once()
        mock_redis_delete.assert_called_once_with(redis_key)
        mock_commit.assert_called_once()  # Проверка, что commit был вызван

        # Reset mocks before next test case
        mock_execute.reset_mock()
        mock_redis_delete.reset_mock()
        mock_commit.reset_mock()

        # Case 2: Users model (test with the actual Users class)
        await delete_single_object_by_id(session, object_id, redis_key, Parents)

        mock_execute.assert_called()
        mock_redis_delete.assert_called_with(redis_key)
        mock_commit.assert_called()
