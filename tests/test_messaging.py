import importlib
import sios_messaging as messaging


def test_inmemory_roundtrip():
    importlib.reload(messaging)  # reset queues
    intent = {"intent": "echo", "intent_id": "x"}
    messaging.send_intent(intent)
    intents = list(messaging.receive_intents())
    assert intents == [intent]
    messaging.publish_response({"status": "ok"})
    responses = list(messaging.receive_responses())
    assert responses == [{"status": "ok"}]
