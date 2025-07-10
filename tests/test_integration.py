import threading
import time
from agent_core import AgentCore
import sios_messaging as messaging


def run_core(core):
    core.loop()


def test_end_to_end():
    core = AgentCore()
    t = threading.Thread(target=run_core, args=(core,), daemon=True)
    t.start()
    intent = {"intent": "echo", "args": "hello", "intent_id": "1"}
    messaging.send_intent(intent)
    time.sleep(0.2)
    responses = list(messaging.receive_responses())
    assert any(resp.get("echo") == "hello" for resp in responses)
    # shutdown observer
    if hasattr(core, "_observer"):
        core._observer.stop()
        core._observer.join()
