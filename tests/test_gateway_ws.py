from fastapi.testclient import TestClient
import intent_gateway
import sios_messaging as messaging

client = TestClient(intent_gateway.app)

def test_websocket_response(monkeypatch):
    resp_data = {"status": "ok", "echo": "hi", "intent_id": "123"}
    def fake_wait(intent_id, timeout=30.0):
        return resp_data
    monkeypatch.setattr(intent_gateway, "_wait_for_response", fake_wait)
    data = {"intent": "echo", "args": "hi", "intent_id": "123"}
    monkeypatch.setattr(messaging, "send_intent", lambda x: None)
    with client.websocket_connect("/ws/123") as ws:
        # send intent first
        client.post("/intents", json=data)
        result = ws.receive_json()
        assert result == resp_data

