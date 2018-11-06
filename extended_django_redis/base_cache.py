from django.core.cache.backends.base import BaseCache
from abc import ABC, abstractmethod


class CacheAndClientSharedInterface(ABC):

  @abstractmethod
  def ttl(self, key, **kwargs):
    """Obtains the time before expiry for a given key, returns 0 if there is no key,
    None if the key does not expire"""
    pass

  @abstractmethod
  def lock(self, key, **kwargs):
    """Obtains a lock for a specific key"""
    pass

  @abstractmethod
  def incr_or_create(self, key, **kwargs):
    """
    Will increment the value in cache. If the value does not exist will set the value in
    cache with the given timeout. Suitable for rate limiting patterns where
    we want to store the number of requests per minute/second.
    """
    pass

  @abstractmethod
  def age(self, key, original_ttl, **kwargs):
    """
    Given the original 'time-to-live' for a key, calculates the age since the key was set.
    """
    pass

  @abstractmethod
  def set_hashmap(self, key, dict, **kwargs):
    """
    Given a dictionary of primative values. Sets the dictionary as a hash map in cache
    or updates an existing dictionary.
    """
    pass

  @abstractmethod
  def get_hashmap(self, key, **kwargs):
    """
    Returns a dictionary of primitives for a given key.
    """
    pass

  @abstractmethod
  def get_hashmap_value(self, key, field, **kwargs):
    """Given a field returns the string hash value"""
    pass


class ExtendedBaseCache(BaseCache, CacheAndClientSharedInterface):
  pass
