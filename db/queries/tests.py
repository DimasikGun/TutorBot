import json
from datetime import datetime
from unittest import IsolatedAsyncioTestCase, main
from unittest.mock import AsyncMock, MagicMock, patch

from db.queries.services import serialize_single_db_item, serialize_many_db_items, deserialize_single_db_item, \
    deserialize_db_items, get_cached_db_item, cache_db_item


class TestSerialization(IsolatedAsyncioTestCase):
    async def test_serialize_single_db_item(self):
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
        self.assertEqual(result, expected_result)

    async def test_serialize_many_db_items(self):
        obj1 = MagicMock()
        obj1.__dict__ = {"id": 1, "name": "Test1"}
        obj2 = MagicMock()
        obj2.__dict__ = {"id": 2, "name": "Test2"}

        result = await serialize_many_db_items([obj1, obj2])
        expected_result = json.dumps([
            json.dumps({"id": 1, "name": "Test1"}),
            json.dumps({"id": 2, "name": "Test2"})
        ])
        self.assertEqual(result, expected_result)

    async def test_deserialize_single_db_item(self):
        obj = {"id": 1, "reg_date": "2023-08-23T00:00:00"}
        result = await deserialize_single_db_item(obj)
        self.assertIsInstance(result['reg_date'], datetime)
        self.assertEqual(result['reg_date'], datetime(2023, 8, 23, 0, 0, 0))

    async def test_deserialize_db_items_single(self):
        json_obj = json.dumps({"id": 1, "reg_date": "2023-08-23T00:00:00"})
        result = await deserialize_db_items(json_obj)
        self.assertIsInstance(result['reg_date'], datetime)
        self.assertEqual(result['reg_date'], datetime(2023, 8, 23, 0, 0, 0))

    async def test_deserialize_db_items_many(self):
        json_obj = json.dumps([
            {"id": 1, "reg_date": "2023-08-23T00:00:00"},
            {"id": 2, "upd_date": "2024-01-01T12:00:00"}
        ])
        result = await deserialize_db_items(json_obj)
        self.assertIsInstance(result[0]['reg_date'], datetime)
        self.assertIsInstance(result[1]['upd_date'], datetime)
        self.assertEqual(result[0]['reg_date'], datetime(2023, 8, 23, 0, 0, 0))
        self.assertEqual(result[1]['upd_date'], datetime(2024, 1, 1, 12, 0, 0))

    @patch('db.queries.services.redis.get', new_callable=AsyncMock)
    async def test_get_cached_db_item(self, mock_redis_get):
        cached_data = json.dumps({"id": 1, "reg_date": "2023-08-23T00:00:00"})
        mock_redis_get.return_value = cached_data
        result = await get_cached_db_item('test_key')
        self.assertIsInstance(result['reg_date'], datetime)
        self.assertEqual(result['reg_date'], datetime(2023, 8, 23, 0, 0, 0))

    @patch('db.queries.services.redis.set', new_callable=AsyncMock)
    @patch('db.queries.services.redis.expire', new_callable=AsyncMock)
    async def test_cache_db_item(self, mock_redis_expire, mock_redis_set):
        obj = MagicMock()
        obj.__dict__ = {"id": 1, "name": "Test1"}
        await cache_db_item(obj, 'test_key')

        mock_redis_set.assert_called_once()
        mock_redis_expire.assert_called_once_with('test_key', 604800)


if __name__ == '__main__':
    main()
