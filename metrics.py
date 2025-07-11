from prometheus_client import Counter, Histogram, start_http_server

intents_received = Counter('intents_received_total', 'Total intents received', ['intent_type'])
intents_success = Counter('intents_success_total', 'Total intents processed successfully', ['intent_type'])
intents_failure = Counter('intents_failure_total', 'Total intents failed', ['intent_type'])
intent_duration = Histogram('intent_execution_duration_seconds', 'Intent execution time', ['intent_type'])


def start_metrics_server(port: int = 8001) -> None:
    try:
        start_http_server(port)
    except OSError:
        pass
