import requests
import json

# Sample input for the financial analysis API
sample_input = {
    "user_id": "user123",
    "income": 8000.0,
    "expenses": [
        {
            "date": "2024-01-15",
            "amount": 2500.0,
            "description": "Monthly rent payment",
            "category": "housing"
        },
        {
            "date": "2024-01-10",
            "amount": 800.0,
            "description": "Grocery shopping at supermarket",
            "category": "food"
        },
        {
            "date": "2024-01-12",
            "amount": 150.0,
            "description": "Uber rides for the week",
            "category": "transport"
        },
        {
            "date": "2024-01-08",
            "amount": 50.0,
            "description": "Netflix subscription",
            "category": "entertainment"
        },
        {
            "date": "2024-01-20",
            "amount": 300.0,
            "description": "Electricity and water bill",
            "category": "utilities"
        },
        {
            "date": "2024-01-25",
            "amount": 200.0,
            "description": "Dining out with friends",
            "category": "food"
        }
    ],
    "investments": [
        {
            "type": "stocks",
            "amount": 15000.0,
            "description": "Equity mutual funds"
        },
        {
            "type": "crypto",
            "amount": 5000.0,
            "description": "Bitcoin and Ethereum"
        },
        {
            "type": "fixed_deposit",
            "amount": 25000.0,
            "description": "Bank fixed deposits"
        }
    ],
    "liabilities": [
        {
            "type": "credit_card",
            "amount": 3000.0,
            "description": "Credit card debt"
        },
        {
            "type": "loan",
            "amount": 50000.0,
            "description": "Car loan"
        }
    ],
    "goals": [
        {
            "name": "Emergency Fund",
            "target": 30000.0,
            "months": 12
        },
        {
            "name": "Vacation",
            "target": 15000.0,
            "months": 6
        },
        {
            "name": "House Down Payment",
            "target": 200000.0,
            "months": 36
        }
    ],
    "as_of": "2024-01-31"
}

def test_api():
    url = "http://localhost:8000/analyze"
    
    try:
        print("Sending request to financial analysis API...")
        print(f"Sample Input: {json.dumps(sample_input, indent=2)}")
        
        response = requests.post(url, json=sample_input)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nResponse: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running on port 8000.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()