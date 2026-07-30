FROM python:3.11-slim

WORKDIR /chaos

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.chaos_api:router", "--host", "0.0.0.0", "--port", "8090"]
