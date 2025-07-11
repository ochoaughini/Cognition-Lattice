# Production-Grade Test Suite

This project includes a growing collection of unit and integration tests. The
notes below outline how the test suite should evolve toward production
readiness and how to validate the system in a real deployment.

## Test Layers

1. **Agent Tests** - cover agent execution, initialization failures and
   sandbox enforcement.  New tests such as `test_timeout_enforcement.py` ensure
   that runaway agents are terminated after the configured timeout.
2. **Orchestration** - use workflow manifests from `tests/fixtures` to verify
   multi-agent SAGA rollbacks and concurrent workflow execution.
3. **Messaging/Broker** - simulate broker disconnects and dead-letter routing to
   guarantee message durability.
4. **Security** - sandboxed agents attempt restricted operations which must be
   denied and logged.
5. **Gateway** - HTTP and WebSocket endpoints deliver intent results reliably
   even when clients reconnect.

## Running Tests

Install dependencies (optionally using a virtual environment):

```bash
pip install -r requirements.txt
```

Run the suite with pytest:

```bash
pytest -q
```

Coverage reports can be generated with:

```bash
pytest --cov
```

## Real‑World Validation

A production‑like environment can be orchestrated with Docker Compose or
Kubernetes. Deploy the API gateway, AgentCore and broker services then submit a
load of intents using an async client (e.g. k6 or Locust). Introduce failures
such as broker restarts or agent file removal to observe recovery behaviour.
Collect Prometheus metrics and logs during the run to verify stability over
extended periods.
