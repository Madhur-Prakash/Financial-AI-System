FROM python:3.10-slim

WORKDIR /finance_ai_system

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

WORKDIR /finance_ai_system/backend

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
