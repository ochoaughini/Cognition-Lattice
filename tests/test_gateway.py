from fastapi.testclient import TestClient
import intent_gateway
import sios_messaging as messaging


def test_create_intent(monkeypatch):
    client = TestClient(intent_gateway.app)
    captured = {}
    def fake_send(intent):
        captured['intent'] = intent
    monkeypatch.setattr(messaging, 'send_intent', fake_send)
    data = {"intent": "echo", "args": "hi", "intent_id": "1"}
    resp = client.post('/intents', json=data)
    assert resp.status_code == 200
    assert captured['intent'] == data


def test_invalid_intent():
    client = TestClient(intent_gateway.app)
    resp = client.post('/intents', json={"args": "hi", "intent_id": "2"})
    assert resp.status_code == 422
