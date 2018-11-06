from unittest import TestCase
from django.core.cache import cache
import time


class DjangoRedisCacheTests(TestCase):
  def setUp(self):
    self.cache = cache

    try:
      self.cache.clear()
    except Exception:
      pass

  def test_incr_or_create(self):
    # initially the key should not exist
    key_to_increment = "test_key"
    result = self.cache.get(key_to_increment, None)
    self.assertIsNone(result)

    # after calling incr_or_create it should exist and be 1
    result = self.cache.incr_or_create(key_to_increment)
    self.assertEqual(result, 1)

    # the ttl should be almost equal to the default ttl
    ttl = self.cache.ttl(key_to_increment)
    self.assertEqual(ttl, self.cache.client._backend.default_timeout)

    # calling incr or create again should increment the value
    result = self.cache.incr_or_create(key_to_increment)
    self.assertEqual(result, 2)

    # we should be able to increment by a custom amount
    result = self.cache.incr_or_create(key_to_increment, delta=5)
    self.assertEqual(result, 7)

    # we should be able to set a custom ttl
    result = self.cache.incr_or_create(key_to_increment, timeout=10)
    ttl = self.cache.ttl(key_to_increment)
    self.assertEqual(ttl, 10)

  def test_age(self):
    test_key = "test_key"
    self.cache.set(test_key, 1, timeout=2)
    self.assertEqual(self.cache.ttl(test_key), 2)
    self.assertEqual(self.cache.age(test_key, 2), 0)
    time.sleep(1)
    self.assertEqual(self.cache.age(test_key, 2), 1)
    time.sleep(1)
    # should return None if the key has expired or does not exist
    self.assertEqual(self.cache.age(test_key, 2), None)

  def test_set_hashmap(self):
    test_key = "test_key"
    hashmap = {"a": 'cat', "b": 'dog'}
    self.cache.set_hashmap(test_key, hashmap)

    # should not set ttl
    self.assertIsNone(self.cache.ttl(test_key), None)

    # setting a hashmap with a non-dictionary should result in an error
    with self.assertRaises(ValueError) as e:
      self.cache.set_hashmap(test_key, {})
    self.assertIn("empty", str(e.exception))

    # setting a hashmap with a non-dictionary should result in an error
    with self.assertRaises(ValueError) as e:
      self.cache.set_hashmap(test_key, "")
    self.assertIn("dict type", str(e.exception))

  def test_get_hashmap(self):
    test_key = "test_key"
    hashmap = {"a": 'cat', "b": 'dog'}
    self.cache.set_hashmap(test_key, hashmap)

    # test result
    result = self.cache.get_hashmap(test_key)
    self.assertIn("a", result)
    self.assertIn("b", result)
    self.assertEqual(result["a"], "cat")
    self.assertEqual(result["b"], "dog")

    # an unset key should return none
    result = self.cache.get_hashmap("unset")
    self.assertEqual(result, {})

  def test_get_hashmap_value(self):
    test_key = "test_key"
    hashmap = {"a": 'cat', "b": 'dog'}
    self.cache.set_hashmap(test_key, hashmap)

    # retrieve a specific value
    self.assertEqual(self.cache.get_hashmap_value(test_key, "a"), "cat")
    self.assertEqual(self.cache.get_hashmap_value(test_key, "b"), "dog")

    # an unknown value should return None
    self.assertEqual(self.cache.get_hashmap_value(test_key, "c"), None)
