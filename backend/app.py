from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
from models import ExpenditureEntry, InsightRequest,ChatRequest, ChatResponse, FullAnalysisRequest
from master_agent import MasterAgent

load_dotenv()

app = FastAPI(title="Financial AI System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize master agent (handles all routing)
master_agent = MasterAgent()

@app.get("/")
async def root():
    return {"message": "Financial AI System API"}

@app.post("/analyze-expenditure", response_model=ChatResponse)
async def analyze_expenditure(entries: List[ExpenditureEntry]):
    """Analyze user expenditure data - routes through master agent"""
    if not entries:
        raise HTTPException(status_code=400, detail="No expenditure entries provided")
    
    try:
        request = ChatRequest(
            message="Analyze my spending data",
            expenditure_data=entries
        )
        response = master_agent.process_user_input(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/generate-insights", response_model=ChatResponse)
async def generate_insights(request: InsightRequest):
    """Generate insights from expenditure analysis - routes through master agent"""
    try:
        chat_request = ChatRequest(
            message="Generate financial insights and recommendations",
            user_context=request.user_context
        )
        response = master_agent.process_user_input(chat_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@app.post("/full-analysis", response_model=ChatResponse)
async def full_analysis(request: FullAnalysisRequest):
    """Complete analysis pipeline - routes through master agent"""
    if not request.entries:
        raise HTTPException(status_code=400, detail="No expenditure entries provided")
    
    try:
        chat_request = ChatRequest(
            message="Analyze my spending and provide insights",
            user_context=request.user_context,
            expenditure_data=request.entries
        )
        response = master_agent.process_user_input(chat_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full analysis failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Master agent endpoint for handling all types of financial queries"""
    try:
        response = master_agent.process_user_input(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")