#!/bin/bash

# Creates venv if it doesn't exist in the directory where src folder resides
# also installs dependencies if venv is not found, 
# if venv exists, nothing happens.

if command -v python3 >/dev/null 2>&1; then
    python=python3
elif command -v python >/dev/null 2>&1; then
    python=python
else
    echo ">>> No suitable Python interpreter found. Try running `python` or `python3` to confirm your installation"
    exit 1
fi

VENV_DIR="$(dirname "$CURRENT_DIR")"

VENV_BIN="$VENV_DIR/venv/bin/activate"

if [ ! -f $VENV_BIN ]; then
    echo ">>> Unable to locate $VENV_BIN, creating venv..."
    $python -m venv $VENV_DIR/venv
    if [ $? -ne 0 ]; then
        echo ">>> Failed to create virtual environment."
        exit 1
    fi
    
    source $VENV_DIR/venv/bin/activate
    echo ">>> Installing dependencies"
    pip install -r $VENV_DIR/requirements.txt && echo "python environment setup complete"
    deactivate
else
    echo ">>> venv is installed, skipping venv creation."
fi