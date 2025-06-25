from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import chatbot
import uuid

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    session_id: str | None = None

@app.get("/chat")
async def chat_get(prompt: str = Query(...), session_id: str = Query(default=None)):
    try:
        session_id = session_id or str(uuid.uuid4())
        response = chatbot.res(prompt, session_id)
        return {"response": response.text, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())
        response = chatbot.res(request.prompt, session_id)
        return {"response": response.text, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
