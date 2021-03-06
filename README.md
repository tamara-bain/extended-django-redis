## Extended Django Redis

This module adds additional functionality to django redis' backend including the following methods:

#### Set Hashmap
`set_hashmap(key, dictionary, **kwargs)`
Implements [hmset](https://redis.io/commands/hmset)
This will automatically serialize non-integer values just like django redis cache's 'set'.
By default it stores a `_last_set: timestamp` field that contains a timestamp of when the field was last set.
This field is popped off when retrieving the entire hashmap with get_hashmap
and only accessible through `get_hashmap_value`.
Note: Fields are always strings

#### Delete and Set Hashmap
`delete_and_set_hashmap(self, key, dict, **kwargs):`
Same as set hashmap but deletes the existing hashmap in an atomic operation
before setting the new hashmap. If the key doesn't exist the deletion fails silently.

#### Get Hashmap 
`get_hashmap(key, **kwargs)`
Implements [hgetall](https://redis.io/commands/hgetall). Returns an empty hashmap if none exists.

#### Get Hashmap Value
`get_hashmap_value(key, field, **kwargs)`
Implements [hget](https://redis.io/commands/hget)
NOTE: Fields are always strings

#### Age
`age(key, original_ttl, **kwargs)`
The age of the key calculated from [ttl](https://redis.io/commands/ttl) and the original ttl given when the key was set.
Returns None if the key never expires.

#### Counter
`counter(self, key, **kwargs)`
Alternative to incr which atomically incrments and sets the expiry for a value. If the value does not exist it
initializes it at 0 and then increments it. Made to cover the counter pattern described here (https://redis.io/commands/incr#pattern-counter)


### Running Tests

1. Install the development requirements using the requirements.txt file:

    `pip install -r requirements.txt`

2. Start redis listening on default socket 127.0.0.1:6379
   If you are on a mac this is a good tutorial: https://medium.com/@petehouston/install-and-config-redis-on-mac-os-x-via-homebrew-eb8df9a4f298

3. After this, run this command:

    `python ./tests/run.py`
