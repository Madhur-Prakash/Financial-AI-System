import os
from langchain_groq import ChatGroq
from typing import List, Dict, Any
from models import ExpenditureEntry, ExpenditureAnalysis, InsightResponse
from collections import defaultdict
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json

class ExpenditureAnalyzer:
    def __init__(self):
        self.client = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile")

    def analyze_expenditure(self, entries: List[ExpenditureEntry]) -> ExpenditureAnalysis:
        total_spending = sum(entry.amount for entry in entries)
        
        # Category breakdown
        category_breakdown = defaultdict(float)
        for entry in entries:
            category_breakdown[entry.category] += entry.amount
        
        # Spending patterns
        spending_patterns = {
            "avg_transaction": total_spending / len(entries) if entries else 0,
            "highest_category": max(category_breakdown.items(), key=lambda x: x[1])[0] if category_breakdown else "",
            "transaction_count": len(entries),
            "categories_count": len(category_breakdown)
        }
        
        # Generate analysis summary
        analysis_summary = self._generate_analysis_summary(total_spending, category_breakdown, spending_patterns)
        print("Analysis Summary:", analysis_summary)
        
        return ExpenditureAnalysis(
            total_spending=total_spending,
            category_breakdown=dict(category_breakdown),
            spending_patterns=spending_patterns,
            analysis_summary=analysis_summary
        )
    
    def _generate_analysis_summary(self, total: float, categories: Dict[str, float], patterns: Dict[str, Any]):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
            """You are a financial analyst. You will analyze the following financial data:

                Total Spending: ${total}
                Category Breakdown: {category_breakdown}
                Spending Patterns: {spending_patterns}

                Please provide a brief analysis summary."""
                            ),
                            ("user", "Analyze expenditure")
                        ])

        try:
            chain = prompt | self.client | StrOutputParser()
            response = chain.invoke({
                "total": f"{total:.2f}",
                "category_breakdown": json.dumps(categories, indent=2),
                "spending_patterns": json.dumps(patterns, indent=2)
            })
            return response
        except Exception as e:
            print(f"LLM analysis summary generation failed: {str(e)}")
            return "The expenditure analysis has been completed."

class InsightsAgent:
    def __init__(self):
        self.client = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile")
    
    def generate_insights(self, analysis: ExpenditureAnalysis, user_context: str = "") -> InsightResponse:
        prompt = ChatPromptTemplate.from_messages([
            ("system",
        """You are a financial analyst. You will analyze the following financial data and provide insights:
        
            Total Spending: {total_spending}
            Category Breakdown: {category_breakdown}
            Spending Patterns: {spending_patterns}
            Analysis Summary: {analysis_summary}
            User Context: {user_context}

            Please provide a JSON response with:
            1. "insights": List of 3-5 key insights about spending behavior
            2. "recommendations": List of 3-5 actionable recommendations
            3. "financial_score": Score from 1-100 based on spending health
            4. "summary": Brief overall summary

            Format as valid JSON only."""
                    ),
                        ("user", "Generate financial insights")
                    ])
        
        try:
            chain = prompt | self.client | StrOutputParser()
            response = chain.invoke({
                "total_spending": f"${analysis.total_spending:.2f}",
                "category_breakdown": json.dumps(analysis.category_breakdown, indent=2),
                "spending_patterns": json.dumps(analysis.spending_patterns, indent=2),
                "analysis_summary": analysis.analysis_summary,
                "user_context": user_context
            })
            print("LLM Insights Response:", response)
            return self._parse_llm_response(response)
    
        except Exception as e:
            return self._fallback_insights(analysis)
    
    def _parse_llm_response(self, response: str) -> InsightResponse:
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            data = json.loads(json_str)
            
            return InsightResponse(
                insights=data.get("insights", []),
                recommendations=data.get("recommendations", []),
                financial_score=data.get("financial_score", 50),
                summary=data.get("summary", "Analysis completed")
            )
        except:
            return InsightResponse(
                insights=["Unable to parse AI response"],
                recommendations=["Please try again"],
                financial_score=50,
                summary="Error processing AI response"
            )
    
    def _fallback_insights(self, analysis: ExpenditureAnalysis) -> InsightResponse:
        insights = [
            f"Your total spending is ${analysis.total_spending:.2f}",
            f"You have {analysis.spending_patterns['categories_count']} spending categories",
            f"Your highest spending category is {analysis.spending_patterns['highest_category']}"
        ]
        
        recommendations = [
            "Track your expenses regularly",
            "Set budget limits for each category",
            "Review and optimize your highest spending categories"
        ]
        
        score = min(100, max(10, int(100 - (analysis.total_spending / 1000) * 10)))
        
        return InsightResponse(
            insights=insights,
            recommendations=recommendations,
            financial_score=score,
            summary="Basic analysis completed with fallback insights"
        )