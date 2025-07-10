# Symbiotic Intelligence Operating System (S.I.O.S.)

This repository contains a prototype implementation of the S.I.O.S. architecture.
It provides a minimal framework for running autonomous coding agents on a local
machine while communicating with remote planners like OpenAI Codex.

## Components

- `bootstrap_env.sh` – sets up a Python virtual environment with required
  packages.
- `agent_core.py` – central orchestrator that loads agents and executes JSON
  intents from `cognition_lattice/intents`.
- `codex_link.py` – helper script for creating intent files (simulating Codex).
- `retrovector_bridge.py` – placeholder for dynamic communication routing.
- `agentfeed_twitter.py` – posts short status updates to Twitter using Tweepy.
- `multi_agent_harmonizer.py` – runs multiple agents on the same intent.
- `cognition_lattice/agents/` – directory for individual agent implementations.
  An example `EchoAgent` is provided.

Intents are JSON files describing an action. When placed in the
`cognition_lattice/intents` directory they are executed and the result written to
`cognition_lattice/responses`.
