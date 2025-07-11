import time
import httpx
import requests
from prometheus_client import REGISTRY

import metrics


def test_metrics_endpoint(tmp_path):
    port = 9000
    metrics.start_metrics_server(port=port)
    metrics.intents_received.labels(intent_type="echo").inc()
    time.sleep(0.1)
    resp = requests.get(f"http://localhost:{port}")
    assert resp.status_code == 200
    assert b"intents_received_total" in resp.content


def test_agent_metrics_exposed(tmp_path):
    port = 9001
    metrics.start_metrics_server(port=port)
    before = REGISTRY.get_sample_value("intent_success_total", {"agent": "EchoAgent"}) or 0
    metrics.intent_success.labels(agent="EchoAgent").inc()
    time.sleep(0.1)
    resp = httpx.get(f"http://localhost:{port}/metrics")
    assert resp.status_code == 200
    assert "intent_success_total" in resp.text
    after = REGISTRY.get_sample_value("intent_success_total", {"agent": "EchoAgent"})
    assert after - before == 1
