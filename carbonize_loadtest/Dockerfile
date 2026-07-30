FROM grafana/k6:latest AS k6-base

FROM python:3.11-slim

COPY --from=k6-base /usr/bin/k6 /usr/bin/k6

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /loadtest
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "python/runner.py"]
