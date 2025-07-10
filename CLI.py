#!/usr/bin/env python3
"""Command line interface for S.I.O.S."""

import argparse
from pprint import pprint

from codex_link import create_intent


def main() -> None:
    parser = argparse.ArgumentParser(description="S.I.O.S. CLI")
    sub = parser.add_subparsers(dest="command")

    new_intent = sub.add_parser("intent", help="create new intent")
    new_intent.add_argument("type")
    new_intent.add_argument("args", nargs="?", default="")

    args = parser.parse_args()
    if args.command == "intent":
        path = create_intent(args.type, args.args)
        print(f"Created {path}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
