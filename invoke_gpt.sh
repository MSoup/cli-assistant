#!/bin/bash

function fail {
    printf 'Error: %s\n' "$1" >&2 ## Send message to stderr.
    exit "${2-1}" ## Return a code specified by $2, or 1 by default.
}

GPT_APP_PATH=$1

# Safeguard against no venv setup
if [ ! -f "$GPT_APP_PATH/venv/bin/activate" ]; then
    fail "Unable to locate: $GPT_APP_PATH/venv/bin/activate"
fi

prompt() {
    source $GPT_APP_PATH/venv/bin/activate
    python3 $GPT_APP_PATH/src/app.py "$@"
    deactivate
}