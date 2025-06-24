from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import chatbot
import redis
import uuid

app = FastAPI()

# Redis setup
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

class ChatRequest(BaseModel):
    prompt: str
    session_id: str | None = None  # Optional session tracking

# 🔁 New function: Get + update full conversation (User + Assistant)
def update_history(session_id: str, user_msg: str, assistant_msg: str, max_len: int = 10):
    key = f"session:{session_id}"

    # Add both messages
    r.rpush(key, f"USER: {user_msg}", f"ASSISTANT: {assistant_msg}")

    # Trim if too long
    r.ltrim(key, max(-1, -max_len * 2), -1)  # 2 lines per turn

    # Fetch updated history
    history = r.lrange(key, 0, -1)
    return history

@app.get("/chat")
async def chat_get(prompt: str = Query(...), session_id: str = Query(default=None)):
    try:
        session_id = session_id or str(uuid.uuid4())
        key = f"session:{session_id}"

        # Get existing history
        history = r.lrange(key, 0, -1)

        # Generate response with full history
        response = chatbot.res(prompt, history)

        # Store both user and assistant messages
        update_history(session_id, prompt, response.text)

        return {"response": response.text, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())
        key = f"session:{session_id}"

        # Get current history
        history = r.lrange(key, 0, -1)

        # Generate response
        response = chatbot.res(request.prompt, history)

        # Save both user and assistant messages
        update_history(session_id, request.prompt, response.text)

        return {"response": response.text, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
