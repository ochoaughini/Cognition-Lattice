#!/bin/bash
# Bootstrap development environment for S.I.O.S.
set -e

if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Please install Homebrew first." >&2
    exit 1
fi

brew install python@3.11 git >/dev/null
python3 -m venv sios_env
source sios_env/bin/activate

pip install --upgrade pip >/dev/null
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu >/dev/null
pip install pandas numpy matplotlib scipy scikit-learn opencv-python pytesseract requests aiohttp websockets gitpython tweepy flask fastapi uvicorn rich click >/dev/null

echo "source $(pwd)/sios_env/bin/activate" >> ~/.bashrc

cat <<EOS
Environment setup complete.
Activate with: source sios_env/bin/activate
Run agent_core.py to start the agent.
EOS
