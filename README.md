# Financial AI System

🤖 **Intelligent Financial Analysis & Advisory System**

A comprehensive FastAPI backend that provides AI-powered financial analysis, personalized insights, and multi-domain financial advice through a unified chat interface.

## 🚀 Quick Start

1. Clone the repository
```bash
git clone https://github.com/Madhur-Prakash/Financial-AI-System-V2.git
cd financial_ai_system_v2
```

2. Create virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Copy the .env.sample file to .env and fill in the required values.
```

5. Start the server
```bash
cd backend
uvicorn app:app --port 8000 --reload
```

**API Documentation**: `http://localhost:8000/docs`

## 🎯 Key Features

- **🤖 Master Agent**: Intelligent query classification and routing
- **📊 Expenditure Analysis**: Automated spending pattern analysis
- **💡 AI Insights**: Personalized financial recommendations using Groq LLM
- **🎯 Multi-Domain Advice**: Tax, investment, revenue, and general financial guidance
- **🔄 Unified API**: Single endpoint handles all query types
- **⚡ High Performance**: FastAPI with async processing

## 📖 Documentation

### 📚 **[Complete Documentation →](./docs/README.md)**

| Document | Description | Audience |
|----------|-------------|----------|
| **[System Overview](./docs/system-overview.md)** | High-level system capabilities and benefits | Everyone |
| **[Frontend Integration](./docs/frontend-integration.md)** | Complete integration guide with examples | Frontend Developers |
| **[API Reference](./docs/api-reference.md)** | Detailed API documentation | All Developers |
| **[Architecture Deep Dive](./docs/architecture.md)** | Technical architecture and design patterns | Backend Developers |
| **[Setup & Deployment](./docs/setup-deployment.md)** | Installation, configuration, and deployment | DevOps/Developers |
| **[Examples & Use Cases](./docs/examples.md)** | Real-world implementation examples | All Developers |

## 🔥 Quick Examples

### Simple Chat Integration
```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "How can I save money on groceries?",
    user_context: "College student"
  })
});

const data = await response.json();
console.log(data.response); // AI-generated advice
console.log(data.query_type); // "insights_generation"
```

### Expenditure Analysis
```javascript
const expenses = [
  { amount: 50, category: "food", description: "Groceries", date: "2024-01-15T10:00:00" },
  { amount: 30, category: "transport", description: "Bus fare", date: "2024-01-15T08:00:00" }
];

const analysis = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Analyze my spending patterns",
    expenditure_data: expenses
  })
});
```

## 🏗️ System Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Frontend   │◄──►│   FastAPI    │◄──►│  Groq LLM   │
│ (Any Tech)  │    │   Backend    │    │ (AI Models) │
└─────────────┘    └──────┬───────┘    └─────────────┘
                          │
                   ┌──────▼──────┐
                   │ Master Agent│
                   │  (Router)   │
                   └──────┬──────┘
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Expenditure  │ │   Insights   │ │  Financial   │
│   Analyzer   │ │    Agent     │ │   Advisors   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 🎯 Query Types Supported

| Type | Description | Example Query |
|------|-------------|---------------|
| **expenditure_analysis** | Spending pattern analysis | "Analyze my expenses" |
| **insights_generation** | Financial recommendations | "How can I save money?" |
| **tax_advice** | Tax planning and tips | "What can I deduct?" |
| **investment_advice** | Investment guidance | "Should I buy stocks?" |
| **revenue_analysis** | Income optimization | "How to increase revenue?" |
| **general_chat** | General financial questions | "What is compound interest?" |

## 🚀 Getting Started by Role

### 👨‍💻 **Frontend Developers**
1. **[Frontend Integration Guide](./docs/frontend-integration.md)** - Complete setup with React/JS examples
2. **[API Reference](./docs/api-reference.md)** - Endpoint documentation
3. **[Examples](./docs/examples.md)** - Real-world implementation patterns

### 🏗️ **Backend Developers** 
1. **[Architecture Deep Dive](./docs/architecture.md)** - System design and patterns
2. **[Setup & Deployment](./docs/setup-deployment.md)** - Local and production setup
3. Explore the codebase: `backend/` directory

### 📋 **Product Managers**
1. **[System Overview](./docs/system-overview.md)** - Capabilities and benefits
2. **[Examples & Use Cases](./docs/examples.md)** - Real-world applications
3. **[API Reference](./docs/api-reference.md)** - Technical capabilities

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **AI**: Groq LLM, LangChain
- **Validation**: Pydantic
- **Frontend**: React (example provided)
- **Deployment**: Docker, AWS, Heroku ready

## 📞 Support & Contributing

- **Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive guides in `/docs`
- **Examples**: Working code samples included
- **API Docs**: Auto-generated at `/docs` endpoint

---

**Ready to integrate?** Start with the **[Frontend Integration Guide](./docs/frontend-integration.md)** 🚀