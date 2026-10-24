FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir "psycopg[binary]~=3.3"
COPY scripts/ scripts/
# Checks both live apps once and prints up / asleep / down (exit code 1 when an app is down)
ENTRYPOINT ["python", "scripts/health_check.py"]
