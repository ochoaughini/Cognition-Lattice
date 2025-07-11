"""Central configuration for broker clients."""

import os


class BrokerConfig:
    @staticmethod
    def get_url() -> str:
        return os.getenv("BROKER_URL", "redis://localhost:6379/0")
