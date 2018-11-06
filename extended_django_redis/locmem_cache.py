from .base_cache import ExtendedBaseCache
from django.core.cache.backends.locmem import LocMemCache


class ExtendedLocMemCache(LocMemCache, ExtendedBaseCache):

  def incr_or_create(self, key, delta=1, timeout=None, **kwargs):
    pass

  def age(self, key, original_ttl, **kwargs):
    pass

  def set_hash(self, key, hashmap, **kwargs):
    pass

  def get_hash(self, key, **kwargs):
    pass

  def get_hash_value(self, key, field, **kwargs):
    pass

  def get_hash_keys(self, key, **kwargs):
    pass

  def set_hash_fields(self, key, hashmap, **kwargs):
    pass

  def lock(self, key, **kwargs):
    pass
