SECRET_KEY = "django_tests_secret_key"

CACHES = {
    "default": {
        "BACKEND": "extended_django_redis.redis_cache.ExtendedRedisCache",
        "LOCATION": [
            "redis://127.0.0.1:6379?db=1",
            "redis://127.0.0.1:6379?db=1",
        ],
        "KEY_PREFIX": "test-prefix",
    },
    "locmem": {
        'BACKEND': 'extended_django_redis.locmem_cache.ExtendedLocMemCache',

    }
}

INSTALLED_APPS = (
    "django.contrib.sessions",
)

SETTINGS_DICT = {
    "INSTALLED_APPS": INSTALLED_APPS,
    "CACHES": CACHES,
    "SECRET_KEY": SECRET_KEY
}