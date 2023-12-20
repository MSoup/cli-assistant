#!/bin/bash

# Creates venv if it doesn't exist in the directory where ask.py resides
# also installs dependencies if venv is not found, 
# if venv exists, nothing happens.

VENV_DIR="$(dirname "$CURRENT_DIR")"

VENV_BIN="$VENV_DIR/venv/bin/activate"

if [ ! -f $VENV_BIN ]; then
    echo "...Unable to locate: $VENV_BIN, creating venv"
    python3 -m venv $VENV_DIR/venv
    source $VENV_DIR/venv/bin/activate
    echo "...Installing dependencies"
    pip install -r $VENV_DIR/requirements.txt && echo "python environment setup complete"
    deactivate
else
    echo "venv install confirmed, skipping venv creation..."
fi