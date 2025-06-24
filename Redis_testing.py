import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# List all keys
keys = r.keys("session:*")
print("Keys:", keys)

# Print data from each session
for key in keys:
    print(f"\nHistory for {key}:")
    history = r.lrange(key, 0, -1)
    for line in history:
        print(line)