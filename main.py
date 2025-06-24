from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import os
import chatbot
app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str


@app.get("/chat")
async def chat_get(prompt: str = Query(...)):
    try:
        response = chatbot.res(prompt)
        return {"response": response.text}  # ⚠️ Note: .text, not .text()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = chatbot.res(request.prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
