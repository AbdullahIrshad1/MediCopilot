# File: backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.utils import get_medical_advice, fetch_history

app = FastAPI(title="MediCopilot API")

# Allow all origins for demo — restrict this in production
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str

@app.post("/query")
async def ask_medicopilot(query: Query):
    try:
        reply = get_medical_advice(query.message)
        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # ✅ Fixed here

@app.get("/history")
def get_recent_history():
    try:
        rows = fetch_history()
        history = [{"timestamp": t, "user_query": q, "response": r} for t, q, r in rows]
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
