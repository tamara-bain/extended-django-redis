from django_redis.cache import RedisCache, omit_exception
from .base_cache import ExtendedBaseCache


class ExtendedRedisCache(RedisCache, ExtendedBaseCache):

  def __init__(self, server, params):
    options = params.setdefault("OPTIONS", {})
    options.setdefault("CLIENT_CLASS", "extended_django_redis.client.DefaultClient")
    super().__init__(server, params)

  @omit_exception
  def counter(self, key, **kwargs):
    return self.client.counter(key, **kwargs)

  @omit_exception
  def age(self, key, original_ttl, **kwargs):
    return self.client.age(key, original_ttl, **kwargs)

  @omit_exception
  def set_hashmap(self, key, hashmap, **kwargs):
    return self.client.set_hashmap(key, hashmap, **kwargs)

  @omit_exception
  def get_hashmap(self, key, **kwargs):
    return self.client.get_hashmap(key, **kwargs)

  @omit_exception
  def get_hashmap_value(self, key, field, **kwargs):
    return self.client.get_hashmap_value(key, field, **kwargs)

  @omit_exception
  def set_hashmap_values(self, key, hashmap, **kwargs):
    return self.client.set_hashmap_values(self, key, hashmap, **kwargs)

  @omit_exception
  def delete_and_set_hashmap(self, key, hashmap, **kwargs):
      return self.client.delete_and_set_hashmap(key, hashmap, **kwargs)

