import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from dotenv import load_dotenv
from models.model import UserFinanceInput, Transaction
from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq  

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY is None:
    raise RuntimeError("Set GROQ_API_KEY environment variable")

# Initialize Groq LLM (choose an appropriate model name available to your account)
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY, temperature=0.2, max_tokens=512)

def categorize_transaction(t: Transaction) -> str:
    desc = t.description.lower()
    if any(x in desc for x in ("rent", "house", "landlord", "apartment")):
        return "housing"
    if any(x in desc for x in ("uber", "ola", "taxi", "cab")):
        return "transport"
    if any(x in desc for x in ("grocery", "supermarket", "bigbasket", "dmart")):
        return "food"
    if any(x in desc for x in ("netflix", "spotify", "prime", "movie", "entertainment")):
        return "entertainment"
    if "salary" in desc or "invoice" in desc:
        return "income"
    return t.category or "other"

def summarize_expenses(expenses: List[Transaction]) -> Dict[str, float]:
    summary = {}
    for t in expenses:
        cat = categorize_transaction(t)
        summary.setdefault(cat, 0.0)
        summary[cat] += abs(t.amount)
    return summary

# ---- Sub-agents ----
def data_parser_agent(payload: UserFinanceInput) -> Dict[str, Any]:
    parsed = {
        "user_id": payload.user_id,
        "income": payload.income,
        "as_of": payload.as_of,
        "expenses_raw": [t.dict() for t in payload.expenses],
    }
    parsed["expenses_by_category"] = summarize_expenses(payload.expenses)
    parsed["investments"] = payload.investments or []
    parsed["liabilities"] = payload.liabilities or []
    parsed["goals"] = payload.goals or []
    return parsed

def expense_analysis_agent(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    expenses_by_cat = parsed_data.get("expenses_by_category", {})
    income = parsed_data.get("income", 0.0)
    total_expenses = sum(expenses_by_cat.values())
    savings = income - total_expenses
    ratios = {k: (v / income * 100 if income > 0 else 0.0) for k, v in expenses_by_cat.items()}
    top_cats = sorted(expenses_by_cat.items(), key=lambda kv: kv[1], reverse=True)[:3]
    recommendations = []
    if ratios.get("housing", 0) > 40:
        recommendations.append("Housing >40% of income. Consider cheaper housing or refinance.")
    if ratios.get("food", 0) > 20:
        recommendations.append("Food >20% of income. Consider meal planning and grocery budgets.")
    if savings < 0:
        recommendations.append("Expenses exceed income — immediate action needed.")
    return {
        "total_expenses": total_expenses,
        "savings": savings,
        "ratios_percent": ratios,
        "top_categories": top_cats,
        "recommendations": recommendations
    }

def investment_advisor_agent(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    investments = parsed_data.get("investments", [])
    allocations = {}
    for inv in investments:
        typ = inv.get("type", "unknown").lower()
        amt = float(inv.get("amount", 0) or 0)
        allocations.setdefault(typ, 0.0)
        allocations[typ] += amt
    total = sum(allocations.values())
    allocations_pct = {k: (v/total*100 if total>0 else 0.0) for k,v in allocations.items()}
    advice = []
    if allocations_pct.get("crypto", 0) > 40:
        advice.append("High crypto exposure — consider reducing to limit volatility.")
    if parsed_data.get("savings", 0) < parsed_data.get("income", 0) * 3:
        advice.append("Emergency fund seems low — aim for 3-6 months of expenses in liquid savings.")
    return {"allocations": allocations, "allocations_percent": allocations_pct, "advice": advice}

# ---- Groq LLM summarizer (via LangChain LLMChain) ----
def llm_summarize(title: str, facts: dict) -> str:
    prompt = PromptTemplate(
    input_variables=["title", "facts"],
    template=(
        "You are an expert Financial Planner AI designed to help users make smarter money decisions.\n"
        "Analyze the user's financial data, which includes details like income, expenses, savings, and spending habits.\n\n"
        "Then, based on your analysis, generate a structured and insightful {title} for the user.\n"
        "The goal is to identify financial patterns, highlight areas of improvement, and create an actionable plan.\n\n"
        "User's Financial Summary:\n{facts}\n\n"
        "Your response should include:\n"
        "1. **Brief Analysis** – A short paragraph summarizing key insights or patterns from the user's financial data.\n"
        "2. **Actionable Plan** – 4 concise bullet points, each representing a clear, practical financial recommendation.\n"
        "3. **Tone** – Keep it professional, encouraging, and easy to understand.\n\n"
        
        "Example Response Format:\n"
        "**Analysis:** You’re spending more than 40% of your income on discretionary categories like entertainment and dining.\n"
        "**Actionable Plan:**\n"
        "• Set a monthly spending limit for non-essentials.\n"
        "• Automate 10% of your income toward savings.\n"
        "• Explore short-term investments for liquidity.\n"
        "• Track expenses weekly using a budgeting app."
    )
)
    chain = prompt | llm
    return chain.invoke({"title": title, "facts": facts})

def financial_planner_agent(parsed_data: Dict[str, Any], expense_analysis: Dict[str,Any], investment_advice: Dict[str,Any]) -> Dict[str,Any]:
    goals = parsed_data.get("goals", [])
    income = parsed_data.get("income", 0.0)
    savings = expense_analysis.get("savings", income)
    monthly_plan = []
    for g in goals:
        name = g.get("name", "Unnamed")
        target = float(g.get("target", 0))
        months = int(g.get("months", 12))
        needed_per_month = target / months if months > 0 else target
        feasible = needed_per_month <= max(0, savings)
        monthly_plan.append({
            "goal": name,
            "target": target,
            "months": months,
            "required_per_month": round(needed_per_month, 2),
            "feasible_with_current_savings": feasible
        })
    recommended_saving_rate = 0.2
    recommended_saving_amount = round(income * recommended_saving_rate, 2)
    planner_text = llm_summarize("Financial Plan Summary", {
        "monthly_savings_available": savings,
        "recommended_saving_rate_pct": recommended_saving_rate*100,
        "recommended_saving_amount": recommended_saving_amount,
        "goals": monthly_plan
    })
    return {"monthly_plan": monthly_plan, "recommended_saving_amount": recommended_saving_amount, "planner_text": planner_text}

# ---- Master agent orchestration ----
def master_agent_run(fin_payload: UserFinanceInput) -> Dict[str,Any]:
    parsed = data_parser_agent(fin_payload)
    expense_analysis = expense_analysis_agent(parsed)
    parsed["savings"] = expense_analysis["savings"]
    investment_advice = investment_advisor_agent(parsed)
    planning = financial_planner_agent(parsed, expense_analysis, investment_advice)
    insights_text = llm_summarize("User Financial Insights", {
        "top_expense_categories": expense_analysis["top_categories"],
        "savings": expense_analysis["savings"],
        "investment_overview": investment_advice.get("allocations_percent"),
        "planner_summary": planning["planner_text"]
    })
    result = {
        "parsed": parsed,
        "expense_analysis": expense_analysis,
        "investment_advice": investment_advice,
        "planning": planning,
        "insights_text": insights_text
    }
    return result