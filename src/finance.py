from fastapi import APIRouter, HTTPException
import os
import sys
import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from helper.utils import master_agent_run
from models.model import UserFinanceInput

router = APIRouter()

@router.post("/analyze", summary="Analyze user's finance and return insights + plan")
async def analyze_finance(payload: UserFinanceInput):
    try:
        result = master_agent_run(payload)
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def health():
    return {"status": "alive", "time": datetime.datetime.utcnow().isoformat()}