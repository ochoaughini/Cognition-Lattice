"""Deployment helper commands."""

import argparse
import subprocess


def deploy_agent(name: str, sandboxed: bool = False) -> None:
    cmd = ["python", "agent_core.py"]
    if sandboxed:
        cmd = ["docker", "run", "--rm", "-v", f"$(pwd):/app", "python:3.10"] + cmd
    subprocess.Popen(cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("deploy-agent")
    parser.add_argument("name")
    parser.add_argument("--sandboxed", action="store_true")
    args = parser.parse_args()
    if args.deploy_agent:
        deploy_agent(args.name, args.sandboxed)
