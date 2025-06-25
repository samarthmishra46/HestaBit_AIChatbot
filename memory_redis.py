import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def update_history(session_id: str, user_msg: str, assistant_msg: str, max_len: int = 10):
    key = f"session:{session_id}"
    r.rpush(key, f"USER: {user_msg}", f"ASSISTANT: {assistant_msg}")
    r.ltrim(key, max(-1, -max_len * 2), -1)
    return r.lrange(key, 0, -1)

def get_history(session_id: str):
    return r.lrange(f"session:{session_id}", 0, -1)
