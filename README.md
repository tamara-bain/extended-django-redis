## Extended Django Redis

This module adds additional functionality to django redis' backend including the following methods:

#### Set Hashmap
`set_hashmap(key, dictionary, **kwargs)`
Implements [hmset](https://redis.io/commands/hmset)

#### Get Hashmap 
`get_hashmap(key, **kwargs)`
Implements [hgetall](https://redis.io/commands/hgetall). Returns an empty hashmap if none exists.

#### Get Hashmap Value
`get_hashmap_value(key, field, **kwargs)`
Implements [hget](https://redis.io/commands/hget)

#### Age
`age(key, original_ttl, **kwargs)`
The age of the key calculated from [ttl](https://redis.io/commands/ttl) and the original ttl given when the key was set

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
