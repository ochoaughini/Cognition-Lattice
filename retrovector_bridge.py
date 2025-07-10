#!/usr/bin/env python3
"""Autonomous channel manager for S.I.O.S."""

import logging
from typing import List


class Route:
    def __init__(self, name: str, priority: int = 0) -> None:
        self.name = name
        self.priority = priority
        self.active = False

    def check(self) -> bool:
        return True


class RetroVectorBridge:
    def __init__(self) -> None:
        self.routes: List[Route] = []

    def add_route(self, route: Route) -> None:
        self.routes.append(route)
        self.routes.sort(key=lambda r: r.priority, reverse=True)

    def get_active_route(self) -> Route:
        for route in self.routes:
            if route.check():
                route.active = True
                return route
        raise RuntimeError("No active route available")


def demo() -> None:
    bridge = RetroVectorBridge()
    bridge.add_route(Route("local", priority=1))
    active = bridge.get_active_route()
    logging.info("Using route %s", active.name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo()
