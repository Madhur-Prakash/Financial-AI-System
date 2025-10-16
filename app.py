from fastapi import FastAPI
from src.finance import router as finance_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Multi-Agent Financial Planner (Groq)")
app.include_router(finance_router, tags=["finance"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- API endpoints ----
