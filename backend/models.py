from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class QueryType(str, Enum):
    EXPENDITURE_ANALYSIS = "expenditure_analysis"
    INSIGHTS_GENERATION = "insights_generation"
    TAX_ADVICE = "tax_advice"
    INVESTMENT_ADVICE = "investment_advice"
    REVENUE_ANALYSIS = "revenue_analysis"
    GENERAL_CHAT = "general_chat"

class ExpenditureEntry(BaseModel):
    amount: float
    category: str
    description: str
    date: datetime

class ExpenditureAnalysis(BaseModel):
    total_spending: float
    category_breakdown: Dict[str, float]
    spending_patterns: Dict[str, Any]
    analysis_summary: str

class InsightRequest(BaseModel):
    analysis_data: ExpenditureAnalysis
    user_context: str = ""

class InsightResponse(BaseModel):
    insights: List[str]
    recommendations: List[str]
    financial_score: int
    summary: str

class ChatRequest(BaseModel):
    message: str
    user_context: Optional[str] = ""
    expenditure_data: Optional[List[ExpenditureEntry]] = None

class ChatResponse(BaseModel):
    response: str
    query_type: QueryType
    data: Optional[Dict[str, Any]] = None

class FullAnalysisRequest(BaseModel):
    entries: List[ExpenditureEntry]
    user_context: str = ""