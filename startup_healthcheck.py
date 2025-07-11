"""Check dependencies before startup."""

import socket
from sios_messaging.broker_config import BrokerConfig


def check_broker() -> bool:
    url = BrokerConfig.get_url()
    host = url.split("//")[-1].split(":")[0]
    try:
        socket.gethostbyname(host)
        return True
    except socket.error:
        return False
