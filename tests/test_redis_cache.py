from unittest import TestCase
from django.core.cache import cache, caches
import time
import threading

class DjangoRedisCacheTests(TestCase):
  def setUp(self):
    self.cache = cache
    self.default_timeout = self.cache.client._backend.default_timeout

    try:
      self.cache.clear()
    except Exception:
      pass

  def test_counter(self):
    # initially the key should not exist
    key_to_increment = "test_key"
    result = self.cache.get(key_to_increment, None)
    self.assertIsNone(result)

    # after calling incr_or_create it should exist and be 1
    result = self.cache.counter(key_to_increment)
    self.assertEqual(result, 1)

    # the ttl should be almost equal to the default ttl
    ttl = self.cache.ttl(key_to_increment)
    self.assertAlmostEqual(ttl, self.default_timeout, 1)

    # calling incr or create again should increment the value
    result = self.cache.counter(key_to_increment)
    self.assertEqual(result, 2)

    # we should be able to increment by a custom amount
    result = self.cache.counter(key_to_increment, delta=5)
    self.assertEqual(result, 7)

    # we should be able to set a custom ttl
    result = self.cache.counter(key_to_increment, timeout=10)
    ttl = self.cache.ttl(key_to_increment)
    self.assertAlmostEqual(ttl, 10, 1)

  def test_age(self):
    test_key = "test_key"
    self.cache.set(test_key, 1, timeout=2)
    self.assertAlmostEqual(self.cache.ttl(test_key), 2, 1)
    self.assertAlmostEqual(self.cache.age(test_key, 2), 0, 1)
    time.sleep(1)
    self.assertAlmostEqual(self.cache.age(test_key, 2), 1, 1)
    time.sleep(1)
    # should return None if the key has expired or does not exist
    self.assertEqual(self.cache.age(test_key, 2), None)

  def test_set_hashmap(self):
    test_key = "test_key"
    hashmap = {"a": '☢', "b": 'dog', 'c': 3}
    self.cache.set_hashmap(test_key, hashmap)

    # should not set ttl
    self.assertIsNone(self.cache.ttl(test_key), None)

    # setting a hashmap with a non-dictionary should result in an error
    with self.assertRaises(ValueError) as e:
      self.cache.set_hashmap(test_key, "")
    self.assertIn("dict type", str(e.exception))

    # overriding one value should not override all values
    hashmap2 = {"b": "not a dog"}
    self.cache.set_hashmap(test_key, hashmap2)
    result = self.cache.get_hashmap(test_key)
    self.assertEqual(result["a"], "☢")
    self.assertEqual(result["b"], "not a dog")
    self.assertEqual(result["c"], 3)
    return

  def test_get_hashmap(self):
    test_key = "test_key"
    hashmap = {"a": 'cat', "b": 'dog'}
    self.cache.set_hashmap(test_key, hashmap)

    # test result
    result = self.cache.get_hashmap(test_key)
    self.assertIn("a", result)
    self.assertIn("b", result)
    self.assertEqual(result, hashmap)

    # an unset key should return an empty map
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

class DjangoLocMemCacheTests(DjangoRedisCacheTests):
    def setUp(self):
        self.cache = caches['locmem']
        self.default_timeout = 300

        try:
          self.cache.clear()
        except Exception:
          pass

    def test_ttl(self):
        # Test ttl
        self.cache.set("foo", "bar", 10)
        ttl = self.cache.ttl("foo")
        self.assertAlmostEqual(ttl, 10, 1)

        # Test ttl None
        self.cache.set("foo", "foo", timeout=None)
        ttl = self.cache.ttl("foo")
        self.assertEqual(ttl, None)

        # Test ttl with expired key
        self.cache.set("foo", "foo", timeout=-1)
        ttl = self.cache.ttl("foo")
        self.assertEqual(ttl, 0)

        # Test ttl with not existent key
        ttl = self.cache.ttl("not-existent-key")
        self.assertEqual(ttl, 0)

    def test_lock(self):
        lock_key = "foobar"
        lock = self.cache.lock(lock_key)
        result = lock.acquire()
        self.assertEqual(result, True)

        # we should not be able to acquire the lock while another process has it
        lock2 = self.cache.lock(lock_key)
        result = lock2.acquire(blocking=False)
        self.assertEqual(result, False)

        # after releasing we should be able to acquire the lock
        lock.release()
        result = lock2.acquire()
        self.assertEqual(result, True)
        lock2.release()

        # if we run without block = false the process should continue to run until
        # it can obtain a lock
        lock.acquire(blocking=False)
        thread = threading.Thread(target=lock2.acquire)
        thread.start()
        self.assertTrue(thread.isAlive())
        lock.release()
        time.sleep(lock2.sleep)
        # lock2 should have the lock so it should not throw an error
        lock2.release()

        # set a blocking timeout, we should stop trying to acquire the lock after the blocking
        # timeout has passed
        lock.acquire()
        initial_time = time.time()
        lock3 = self.cache.lock(lock_key, blocking_timeout=1)
        result = lock3.acquire()
        self.assertFalse(result)
        self.assertAlmostEqual(initial_time - time.time(), -1, 1)
