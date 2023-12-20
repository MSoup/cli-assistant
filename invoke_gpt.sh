#!/bin/bash

function fail {
    printf 'Error: %s\n' "$1" >&2 ## Send message to stderr.
    exit "${2-1}" ## Return a code specified by $2, or 1 by default.
}

GPT_APP_PATH=$(pwd)

# Safeguard against no venv setup
if [ ! -f "$GPT_APP_PATH/venv/bin/activate" ]; then
    fail "Unable to locate: $GPT_APP_PATH/venv/bin/activate"
fi

ask-gpt() {
    source $GPT_APP_PATH/venv/bin/activate
    python3 $GPT_APP_PATH/ask.py "$@"
    deactivate
}