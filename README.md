# Symbiotic Intelligence Operating System (S.I.O.S.)

This repository contains a prototype implementation of the S.I.O.S. architecture, now enhanced for dynamic module loading, scalable messaging, observability, schema validation, and containerized deployment. It provides a framework for running autonomous coding agents on local or distributed infrastructure, integrating with remote planners like OpenAI Codex.

## Features and Architecture

* **Dynamic Agent Discovery & Hot-Reload**: Agents placed in `cognition_lattice/agents` are discovered and reloaded at runtime using `watchdog`, eliminating the need to restart the core for updates or security patches.
* **Message-Driven Processing**: Intents are no longer polled from disk but enqueued in a broker (e.g., RabbitMQ, Redis Streams, or AWS SQS). The `AgentCore` functions as a consumer, supporting parallel processing and guaranteed once-only delivery with dead-letter queue support.
* **Observability & Metrics**: Prometheus-compatible metrics (intent counts, latencies, error rates) are exposed via an HTTP endpoint. Structured logs are shipped to Elasticsearch/Kibana or Grafana Loki, providing real-time dashboards and alerting.
* **Schema Validation**: Intent payloads adhere to a strict contract defined in JSON Schema or Protocol Buffers. Validation occurs at ingestion, returning structured errors for malformed or version-incompatible messages.
* **Automated Testing**: Comprehensive suite of unit tests for each `BaseAgent` implementation and integration tests for the end-to-end flow, ensuring regression-free evolution.
* **Containerized Deployment**: A Dockerfile and `docker-compose.yaml` orchestrate S.I.O.S. services (message broker, metrics/logs infrastructure, AgentCore), enabling reproducible environments and seamless scaling via Kubernetes or Docker Swarm.
* **API Gateway for Intents**: A lightweight FastAPI service (`intent_gateway.py`) exposes HTTP/WebSocket endpoints for creating and managing intents, adding authentication, tracing metadata, and fine-grained authorization.
* **Multi-Agent Orchestration**: Advanced harmonizer supports SAGA and choreography patterns, allowing agents to coordinate stateful workflows with rollback capabilities and compensating transactions.
* **Memory and Model Registry**: Pluggable memory backends and a dynamic model registry enable agents to share state and load ML models on demand.

## Getting Started

### Prerequisites

* macOS or Linux with Docker and Docker Compose installed
* Homebrew (macOS) or equivalent package manager
* (Optional) Python 3.11 for local venv development

### Local Development with Virtualenv

```bash
# Bootstrap and activate environment
./bootstrap_env.sh

# Install additional development dependencies (if not containerized)
pip install pytest pytest-cov watchdog

# Run unit tests
pytest --cov=cognition_lattice/agents

# Start AgentCore worker
python agent_core.py

# In a separate terminal run the intent gateway
python intent_gateway.py
```

### Running with Docker Compose

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f agent_core gateway

# Scale AgentCore workers
docker-compose up --scale agent_core=3 -d
```

Minimal `docker-compose.yaml` example:

```yaml
version: '3'
services:
  agent_core:
    build: .
    environment:
      - MESSAGE_BROKER=redis
  gateway:
    build: .
    environment:
      - MESSAGE_BROKER=redis
  redis:
    image: redis:7-alpine
```

### Connecting via API Gateway

```bash
# Submit a new intent via HTTP
token=<YOUR_API_TOKEN>
curl -X POST http://localhost:8000/intents \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{"intent": "echo", "args": "Hello World"}'
```

## Project Structure

```
├── agent_core.py               # Core consumer for intent messages
├── intent_gateway.py           # FastAPI gateway for HTTP/WebSocket intents
├── multi_agent_harmonizer.py   # Orchestrates multi-agent workflows
├── retrovector_bridge.py       # Communication router (pluggable channels)
├── agentfeed_twitter.py        # Example status feed integration via Tweepy
├── cognition_lattice/          # Core agents framework
│   ├── agents/                 # Agent modules (hot-reloaded)
│   ├── base_agent.py           # Abstract base class for agents
│   ├── intents/                # (Deprecated polling; for reference)
│   └── responses/              # (Deprecated polling; for reference)
├── sios_messaging/            # Transport abstraction layer
├── metrics.py                  # Prometheus metrics helpers
├── validation.py               # JSON Schema validation utilities
├── schemas/                    # Intent schema definitions
│   └── echo.json               # Example schema for EchoAgent
├── docker-compose.yaml         # Broker, metrics, logs, and AgentCore services
├── Dockerfile                  # Builds AgentCore and dependencies
├── bootstrap_env.sh            # Local Python venv bootstrap script
└── tests/                      # Unit and integration tests
```

## Extensibility

* **Adding Agents**: Create or update modules under `cognition_lattice/agents`, define `intent_types`, and implement `execute()`. The core will auto-discover and reload changes.
* **Schema Definitions**: Extend `schemas/` with JSON Schema or `.proto` files and register in ingestion layer for validation.
* **Metrics & Logging**: Modify the `metrics/` and `logging/` configurations to integrate with your monitoring stack.

## Contributing

Contributions are welcome via GitHub pull requests. Ensure that new features include tests and documentation updates.

---

*Symbiotic Intelligence Operating System — evolving autonomous agents for mission-critical workflows.*
