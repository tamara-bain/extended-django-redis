import time
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django_redis.client import DefaultClient as DjangoRedisDefaultClient
from django_redis.client.default import _main_exceptions
from django_redis.exceptions import ConnectionInterrupted
from .base_client import BaseClient

class DefaultClient(DjangoRedisDefaultClient, BaseClient):


    def counter(self, key, delta=1, timeout=DEFAULT_TIMEOUT, version=None, client=None):
        """
        Increments the given key and sets the expiry in an atomic operation (lua script)

        If timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.
        """
        if client is None:
            client = self.get_client(write=True)

        key = self.make_key(key, version=version)

        if timeout == DEFAULT_TIMEOUT:
            timeout = self._backend.default_timeout

        try:
            lua = """
            local count = redis.call('INCRBY', KEYS[1], ARGV[1])
            redis.call('EXPIRE', KEYS[1], ARGV[2])
            return count
            """
            value = client.eval(lua, 1, key, delta, timeout)
            if value is None:
                raise ValueError("Key '%s' not found" % key)
        except _main_exceptions as e:
            raise ConnectionInterrupted(connection=client, parent=e)

        return value

    def age(self, key, original_ttl, version=None, client=None):
        """
        Calculates the age of an object given the original ttl.
        Returns none if the key never expires.
        """
        ttl = self.ttl(key, version=version, client=client)
        if (ttl == None):
            return None
        return original_ttl - ttl

    def delete_and_set_hashmap(self, key, dictionary, **kwargs):
        self._set_hashmap(key, dictionary, clear_existing=True, **kwargs)

    def set_hashmap(self, key, dictionary, **kwargs):
        self._set_hashmap(key, dictionary, clear_existing=False, **kwargs)

    def _set_hashmap(self, key, dictionary, version=None, client=None, last_set_key="_last_set", clear_existing=False):
        """
        Dictionary values must be strings or numbers.
        """
        if type(dictionary) is not dict:
            raise ValueError("set_hashmap expects dictionary to be a dict type")

        if client is None:
            client = self.get_client(write=True)

        key = self.make_key(key, version=version)

        dictionary = {k: self.encode(v) for k, v in dictionary.items()}

        # store update time, this has the added benefit of
        # letting us save empty dictionaries in cache
        # we pop this off before returning all keys
        dictionary[last_set_key] = self.encode(int(time.time()))

        try:
            if clear_existing:
                list = [item for key in dictionary for item in (key, dictionary[key])]
                lua = """
                redis.call('DEL', KEYS[1])
                local result = redis.call('HMSET', KEYS[1], unpack(ARGV))
                return result
                """
                value = client.eval(lua, 1, key, *list)
            else:
                value = client.hmset(key, dictionary)
        except _main_exceptions as e:
            raise ConnectionInterrupted(connection=client, parent=e)
        return value

    def get_hashmap(self, key, version=None, client=None, decode=True, last_set_key="_last_set"):
        """
        Returns a python dictionary if it exists otherwise {}.
        """
        if client is None:
            client = self.get_client(write=False)

        key = self.make_key(key, version=version)

        try:
            value = client.hgetall(key)
        except _main_exceptions as e:
            raise ConnectionInterrupted(connection=client, parent=e)

        dictionary = {k.decode('utf8'): self.decode(v) for k, v in value.items()}
        dictionary.pop(last_set_key, None)
        return dictionary

    def get_hashmap_value(self, key, field, version=None, client=None):
        """
        Returns they field if it exists, otherwise None
        """
        if client is None:
            client = self.get_client(write=False)

        key = self.make_key(key, version=version)

        try:
            value = client.hget(key, field)
        except _main_exceptions as e:
            raise ConnectionInterrupted(connection=client, parent=e)

        if value is None:
            return None

        return self.decode(value)
