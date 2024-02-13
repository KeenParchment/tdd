"""
Test Cases for Counter Web Service

Create a service that can keep a track of multiple counters
- API must be RESTful - see the status.py file. Following these guidelines, you can make assumptions about
how to call the web service and assert what it should return.
- The endpoint should be called /counters
- When creating a counter, you must specify the name in the path.
- Duplicate names must return a conflict error code.
- The service must be able to update a counter by name.
- The service must be able to read the counter
"""
import json
from unittest import TestCase

# we need to import the unit under test - counter
from src.counter import app

# we need to import the file that contains the status codes
from src import status


class CounterTest(TestCase):
    """Counter tests"""

    def setUp(self):
        self.client = app.test_client()

    def test_create_a_counter(self):
        """It should create a counter"""
        result = self.client.post('/counters/foo')
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_duplicate_a_counter(self):
        """It should return an error for duplicates"""
        self._create_counter_and_assert('bar_duplicate', status.HTTP_201_CREATED)
        result = self.client.post('/counters/bar_duplicate')
        self.assertEqual(result.status_code, status.HTTP_409_CONFLICT)

    def test_read_a_counter(self):
        """It should read a counter"""
        counter_name = 'bar_read'
        self._create_counter_and_assert(counter_name, status.HTTP_201_CREATED)

        result = self.client.get(f'/counters/{counter_name}')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        value = json.loads(result.data)[counter_name]
        self.assertEqual(value, 0)

        no_result = self.client.get('/counters/no_result_read')
        self.assertEqual(no_result.status_code, status.HTTP_404_NOT_FOUND)
        response_data = json.loads(no_result.data)
        self.assertEqual(response_data["error"], "Counter not found")

    def test_update_a_counter(self):
        """It should update a counter"""
        counter_name = 'bar_update'
        self._create_counter_and_assert(counter_name, status.HTTP_201_CREATED)

        base_result = self.client.get(f'/counters/{counter_name}')
        base_value = json.loads(base_result.data)[counter_name]

        update_result = self.client.put(f'/counters/{counter_name}')
        self.assertEqual(update_result.status_code, status.HTTP_200_OK)

        new_result = self.client.get(f'/counters/{counter_name}')
        new_value = json.loads(new_result.data)[counter_name]
        self.assertEqual(new_value, base_value + 1)

        no_result = self.client.put('/counters/no_result_update')
        self.assertEqual(no_result.status_code, status.HTTP_404_NOT_FOUND)
        response_data = json.loads(no_result.data)
        self.assertEqual(response_data["error"], "Counter not found")

    def test_delete_counter(self):
        """It should delete a counter"""
        self.client.post('/counters/delete')

        result = self.client.delete('/counters/delete')
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)

        result = self.client.delete('/counters/empty')
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)

    # helper function
    def _create_counter_and_assert(self, name, expected_status):
        result = self.client.post(f'/counters/{name}')
        self.assertEqual(result.status_code, expected_status)
