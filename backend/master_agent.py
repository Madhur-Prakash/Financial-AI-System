import os
from langchain_groq import ChatGroq
from models import ChatRequest, ChatResponse, QueryType
from agents import ExpenditureAnalyzer, InsightsAgent
import json


class MasterAgent:
    def __init__(self):
        self.client = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile")
        self.expenditure_analyzer = ExpenditureAnalyzer()
        self.insights_agent = InsightsAgent()
        
    def process_user_input(self, request: ChatRequest) -> ChatResponse:
        """Main entry point - intelligently routes user queries to appropriate agents"""
        # Classify the query type using AI
        query_type = self._classify_query(request.message)
        
        # Route to appropriate handler based on query type and available data
        if query_type == QueryType.EXPENDITURE_ANALYSIS:
            if request.expenditure_data:
                return self._handle_expenditure_analysis(request)
            else:
                # No data provided, ask for it or provide general advice
                return ChatResponse(
                    response="To analyze your expenditure, I'll need your spending data. You can provide it in your next message, or I can give you general budgeting advice instead. What would you prefer?",
                    query_type=QueryType.EXPENDITURE_ANALYSIS
                )
        
        elif query_type == QueryType.INSIGHTS_GENERATION:
            return self._handle_insights_request(request)
        
        elif query_type in [QueryType.TAX_ADVICE, QueryType.INVESTMENT_ADVICE, QueryType.REVENUE_ANALYSIS]:
            return self._handle_financial_advice(request, query_type)
        
        else:
            return self._handle_general_chat(request)
    
    def _classify_query(self, message: str) -> QueryType:
        """Use AI to intelligently classify user queries"""
        classification_prompt = f"""
        Classify the following user message into one of these categories:
        - expenditure_analysis: User wants to analyze spending/expenses/budget
        - insights_generation: User wants financial insights, recommendations, or advice
        - tax_advice: User asks about taxes, deductions, or tax planning
        - investment_advice: User asks about investments, stocks, or portfolio
        - revenue_analysis: User asks about income, revenue, or earnings analysis
        - general_chat: General financial questions or conversation
        
        User message: "{message}"
        
        Respond with only the category name (e.g., "expenditure_analysis").
        """
        
        try:
            response = self.client.invoke(classification_prompt)
            classification = response.content.strip().lower()
            print(f"AI Classification: {classification}")
            
            # Map to QueryType enum
            query_mapping = {
                "expenditure_analysis": QueryType.EXPENDITURE_ANALYSIS,
                "insights_generation": QueryType.INSIGHTS_GENERATION,
                "tax_advice": QueryType.TAX_ADVICE,
                "investment_advice": QueryType.INVESTMENT_ADVICE,
                "revenue_analysis": QueryType.REVENUE_ANALYSIS,
                "general_chat": QueryType.GENERAL_CHAT
            }
            
            return query_mapping.get(classification, QueryType.GENERAL_CHAT)
            
        except Exception as e:
            print(f"Classification error: {e}")
            # Fallback to keyword-based classification
            return self._fallback_classify(message)
    
    def _fallback_classify(self, message: str) -> QueryType:
        """Fallback keyword-based classification"""
        message_lower = message.lower()
        
        expenditure_keywords = ["spending", "expense", "expenditure", "analyze", "budget", "spent", "cost"]
        insights_keywords = ["insights", "recommendations", "advice", "help", "tips", "improve", "save"]
        tax_keywords = ["tax", "taxation", "deduction", "filing", "irs", "refund"]
        investment_keywords = ["invest", "investment", "stocks", "portfolio", "returns", "market"]
        revenue_keywords = ["revenue", "income", "earnings", "profit", "salary", "business"]
        
        if any(keyword in message_lower for keyword in expenditure_keywords):
            return QueryType.EXPENDITURE_ANALYSIS
        elif any(keyword in message_lower for keyword in insights_keywords):
            return QueryType.INSIGHTS_GENERATION
        elif any(keyword in message_lower for keyword in tax_keywords):
            return QueryType.TAX_ADVICE
        elif any(keyword in message_lower for keyword in investment_keywords):
            return QueryType.INVESTMENT_ADVICE
        elif any(keyword in message_lower for keyword in revenue_keywords):
            return QueryType.REVENUE_ANALYSIS
        else:
            return QueryType.GENERAL_CHAT
    
    def _handle_expenditure_analysis(self, request: ChatRequest) -> ChatResponse:
        try:
            analysis = self.expenditure_analyzer.analyze_expenditure(request.expenditure_data)
            
            response_text = f"I've analyzed your expenditure data:\n\n"
            response_text += f"• Total Spending: ${analysis.total_spending:.2f}\n"
            response_text += f"• Categories: {len(analysis.category_breakdown)}\n"
            response_text += f"• Top Category: {analysis.spending_patterns.get('highest_category', 'N/A')}\n\n"
            response_text += analysis.analysis_summary
            
            return ChatResponse(
                response=response_text,
                query_type=QueryType.EXPENDITURE_ANALYSIS,
                data=analysis.dict()
            )
        except Exception as e:
            return ChatResponse(
                response=f"Sorry, I couldn't analyze your expenditure data: {str(e)}",
                query_type=QueryType.EXPENDITURE_ANALYSIS
            )
    
    def _handle_insights_request(self, request: ChatRequest) -> ChatResponse:
        """Handle insights generation - use existing InsightsAgent if expenditure data available"""
        
        # If expenditure data is provided, use the full pipeline
        if request.expenditure_data:
            try:
                # First analyze expenditure
                analysis = self.expenditure_analyzer.analyze_expenditure(request.expenditure_data)
                
                # Then generate insights using the InsightsAgent
                insights_response = self.insights_agent.generate_insights(analysis, request.user_context)
                
                # Format response
                response_text = f"Based on your spending data, here are my insights:\n\n"
                response_text += f"**Financial Score: {insights_response.financial_score}/100**\n\n"
                response_text += f"**Key Insights:**\n"
                for insight in insights_response.insights:
                    response_text += f"• {insight}\n"
                response_text += f"\n**Recommendations:**\n"
                for rec in insights_response.recommendations:
                    response_text += f"• {rec}\n"
                response_text += f"\n{insights_response.summary}"
                
                return ChatResponse(
                    response=response_text,
                    query_type=QueryType.INSIGHTS_GENERATION,
                    data={
                        "analysis": analysis.dict(),
                        "insights": insights_response.dict()
                    }
                )
            except Exception as e:
                return ChatResponse(
                    response=f"I had trouble analyzing your data, but here's some general advice: {str(e)}",
                    query_type=QueryType.INSIGHTS_GENERATION
                )
        
        # If no expenditure data, provide general insights using AI
        prompt = f"""
        The user is asking for financial insights: "{request.message}"
        User context: {request.user_context}
        
        Provide personalized financial insights and recommendations in a conversational tone.
        Focus on actionable advice for better financial management.
        Keep it practical and helpful.
        """
        
        try:
            response = self.client.invoke(prompt)
            print(f"Insights AI Response: {response.content}")
            
            return ChatResponse(
                response=response.content,
                query_type=QueryType.INSIGHTS_GENERATION
            )
        except Exception as e:
            print(f"Insights generation error: {e}")
            return ChatResponse(
                response="Here are some general financial insights: Track your expenses regularly, set monthly budgets, and review your spending patterns to identify areas for improvement.",
                query_type=QueryType.INSIGHTS_GENERATION
            )
    
    def _handle_financial_advice(self, request: ChatRequest, query_type: QueryType) -> ChatResponse:
        advice_prompts = {
            QueryType.TAX_ADVICE: "You are a tax advisor. Provide helpful tax advice and tips for the user's question. Be specific and actionable.",
            QueryType.INVESTMENT_ADVICE: "You are an investment advisor. Provide investment guidance and strategies for the user's question. Focus on practical advice.",
            QueryType.REVENUE_ANALYSIS: "You are a financial analyst. Provide revenue analysis and business income insights for the user's question."
        }

        prompt = f"""
        {advice_prompts[query_type]}
        
        User question: "{request.message}"
        User context: {request.user_context}
        
        Provide clear, actionable advice in a conversational tone.
        Include specific steps or recommendations where appropriate.
        Keep it practical and helpful.
        """
        
        try:
            response = self.client.invoke(prompt)
            print(f"Financial Advice AI Response: {response.content}")
            
            return ChatResponse(
                response=response.content,
                query_type=query_type
            )
        except Exception as e:
            print(f"Financial advice error: {e}")
            fallback_responses = {
                QueryType.TAX_ADVICE: "For tax advice, consider consulting with a tax professional. Keep detailed records of your expenses and income throughout the year.",
                QueryType.INVESTMENT_ADVICE: "For investments, consider diversifying your portfolio and investing in low-cost index funds. Always do your research before investing.",
                QueryType.REVENUE_ANALYSIS: "To analyze revenue, track your income sources, monitor trends over time, and identify your most profitable activities."
            }
            
            return ChatResponse(
                response=fallback_responses.get(query_type, "I'm here to help with your financial questions."),
                query_type=query_type
            )
    
    def _handle_general_chat(self, request: ChatRequest) -> ChatResponse:
        prompt = f"""
        The user is asking: "{request.message}"
        User context: {request.user_context}
        
        This appears to be a general financial question. Provide a helpful, conversational response
        related to personal finance, money management, or financial planning.
        Keep it friendly and informative.
        """
        
        try:
            response = self.client.invoke(prompt)
            print(f"General Chat AI Response: {response.content}")
            
            return ChatResponse(
                response=response.content,
                query_type=QueryType.GENERAL_CHAT
            )
        except Exception as e:
            print(f"General chat error: {e}")
            return ChatResponse(
                response="I'm here to help with your financial questions! Feel free to ask about budgeting, investments, taxes, or any other money-related topics.",
                query_type=QueryType.GENERAL_CHAT
            )