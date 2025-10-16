from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uuid
from datetime import datetime

class Transaction(BaseModel):
    date: Optional[str] = None
    amount: float
    description: str
    category: Optional[str] = None

class UserFinanceInput(BaseModel):
    user_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    income: float
    expenses: List[Transaction]
    investments: Optional[List[Dict[str, Any]]] = []
    liabilities: Optional[List[Dict[str, Any]]] = []
    goals: Optional[List[Dict[str, Any]]] = []
    as_of: Optional[str] = Field(default_factory=lambda: datetime.today().isoformat())