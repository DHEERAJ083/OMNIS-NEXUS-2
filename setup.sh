#!/bin/bash
set -e

echo "Setting up Omnis-Nexus Environment..."

# Check python
if ! command -v python3 &> /dev/null; then
    echo "python3 could not be found"
    exit 1
fi

# Create venv
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Install
echo "Installing dependencies..."
./.venv/bin/pip install -r requirements.txt

echo "Setup Complete!"
echo "To run the server manually:"
echo "  ./.venv/bin/python omnis_nexus_server.py"
