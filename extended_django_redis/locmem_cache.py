from .base_cache import ExtendedBaseCache
from django.core.cache.backends.locmem import LocMemCache
import pickle
import time
import uuid

DEFAULT_TIMEOUT = 300

class LockError(Exception):
    pass


class InMemoryLock:
    """
    Redis lock code adapted from redis.lock.Lock
    """

    def __init__(self, cache, key, timeout=None, sleep=0.1, blocking_timeout=None, blocking=True):
        self.cache = cache
        self.key = key
        self.timeout = timeout
        self.sleep = sleep
        self.blocking_timeout = blocking_timeout
        self.blocking = blocking
        self.acquired_token = None

    def __enter__(self):
        # force blocking, as otherwise the user would have to check whether
        # the lock was actually acquired or not.
        self.acquire(blocking=True)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def acquire(self, blocking=None, blocking_timeout=None):
        """
        Returns True once the lock is acquired.
        If ``blocking`` is False, always return immediately. If the lock
        was acquired, return True, otherwise return False.
        ``blocking_timeout`` specifies the maximum number of seconds to
        wait trying to acquire the lock.
        """
        sleep = self.sleep
        token = uuid.uuid1().hex

        if blocking_timeout is None:
            blocking_timeout = self.blocking_timeout

        if blocking is None:
            blocking = self.blocking

        stop_trying_at = None
        if blocking_timeout is not None:
            stop_trying_at = time.time() + blocking_timeout

        while True:
            if self.do_acquire(token):
                self.acquired_token = token
                return True
            if not blocking:
                return False
            if stop_trying_at is not None and time.time() > stop_trying_at:
                return False
            time.sleep(sleep)

    def do_acquire(self, token):
        with self.cache._lock:
            if self.cache._has_key(self.key):
                return False
            self.cache._set(self.key, token, self.timeout)
            return True

    def release(self, ignore_lock_errors=False):
        "Releases the already acquired lock"
        expected_token = self.acquired_token

        if ignore_lock_errors:
            try:
                self.do_release(expected_token)
            except LockError:
                pass
        else:
            self.do_release(expected_token)

    def do_release(self, expected_token):
        if expected_token is None:
            raise LockError("Cannot release an unlocked lock")

        with self.cache._lock:
            lock_value = None
            if self.cache._has_key(self.key):
                lock_value = self.cache._cache[self.key]

            if lock_value != expected_token:
                raise LockError("Cannot release a lock that's no longer owned")
            self.cache._delete(self.key)


class ExtendedLocMemCache(LocMemCache, ExtendedBaseCache):

    def _has_key(self, key):
        if self._has_expired(key):
            self._delete(key)
            return False
        return True

    def lock(self, key, version=None, timeout=DEFAULT_TIMEOUT, sleep=0.1, blocking_timeout=None, **kwargs):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        return InMemoryLock(self, key, timeout=timeout, sleep=sleep, blocking_timeout=blocking_timeout)

    def ttl(self, key, version=None, **kwargs):
        """Obtains the time before expiry for a given key"""
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock:
            if self._cache.get(key, None) is None:
                return 0
            if self._has_expired(key):
                return 0
            exp = self._expire_info.get(key, None)
            if (exp is None):
                return None
            return exp - time.time()

    def counter(self, key, delta=1, timeout=DEFAULT_TIMEOUT, version=None, **kwargs):
        key = self.make_key(key, version=version)
        self.validate_key(key)

        with self._lock:
            # set the value
            if not self._has_key(key):
                pickled = pickle.dumps(delta, pickle.HIGHEST_PROTOCOL)
                self._set(key, pickled, timeout)
                new_value = delta
            else:
                pickled = self._cache[key]
                value = pickle.loads(pickled)
                new_value = value + delta
                pickled = pickle.dumps(new_value, pickle.HIGHEST_PROTOCOL)
            self._set(key, pickled, timeout)
            return new_value

    def age(self, key, original_ttl, version=None, **kwargs):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        exp = self._expire_info.get(key, -1)
        if exp is None:
            return None
        exp -= time.time()
        if exp < 0:
            return original_ttl
        return original_ttl - exp

    def delete_and_set_hashmap(self, key, dictionary, **kwargs):
        self._set_hashmap(key, dictionary, clear_existing=True, **kwargs)

    def set_hashmap(self, key, dictionary, **kwargs):
        self._set_hashmap(key, dictionary, clear_existing=False, **kwargs)

    def _set_hashmap(self, key, hashmap, version=None, last_set_key="_last_set", clear_existing=False, **kwargs):
        key = self.make_key(key, version=version)
        self.validate_key(key)

        if type(hashmap) is not dict:
            raise ValueError("set_hashmap expects dictionary to be a dict type")

        hashmap = {key: pickle.dumps(value, pickle.HIGHEST_PROTOCOL) for key, value in hashmap.items()}

        # store update time
        # we pop this off before returning all keys
        hashmap[last_set_key] = pickle.dumps(int(time.time()), pickle.HIGHEST_PROTOCOL)

        with self._lock:
            if not self._has_key(key):
                self._set(key, hashmap, None)
            dictionary = self._cache[key]
            self._cache.move_to_end(key, last=False)
            if clear_existing:
                dictionary = hashmap
            else:
                dictionary.update(hashmap)
            self._set(key, dictionary, None)

    def get_hashmap(self, key, version=None, last_set_key="_last_set",  **kwargs):
        """
        Returns a python dictionary if it exists otherwise {}.
        """
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock:
            if not self._has_key(key):
                return {}
            dictionary = self._cache[key]
            self._cache.move_to_end(key, last=False)

        dictionary.pop(last_set_key, None)
        dictionary = {key: pickle.loads(value) for key, value in dictionary.items()}
        return dictionary

    def get_hashmap_value(self, key, field, version=None, **kwargs):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock:
            if self._has_expired(key):
                self._delete(key)
                return None
            dictionary = self._cache[key]
            self._cache.move_to_end(key, last=False)
        value = dictionary.get(field, None)
        if value is not None:
            value = pickle.loads(value)
        return value
