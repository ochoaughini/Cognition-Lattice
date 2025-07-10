import time
import requests

import metrics


def test_metrics_endpoint(tmp_path):
    port = 9000
    metrics.start_metrics_server(port=port)
    metrics.intents_received.labels(intent_type="echo").inc()
    time.sleep(0.1)
    resp = requests.get(f"http://localhost:{port}")
    assert resp.status_code == 200
    assert b"intents_received_total" in resp.content
