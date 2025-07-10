FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir fastapi uvicorn jsonschema prometheus_client watchdog
CMD ["python", "agent_core.py"]
