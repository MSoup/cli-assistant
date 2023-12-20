#!/bin/bash

# Set SOURCE_CONFIG_FILE_PATH and CONFIG_FILENAME
SOURCE_CONFIG_FILE_PATH="~"
CONFIG_FILENAME=".zshrc"

# Run script from within the same directory as `ask.py`
CURRENT_DIR=$(pwd)

# Invoke from parent directory
INVOKE_SCRIPT="$(dirname "$CURRENT_DIR")/invoke_gpt.sh"

# Ensure ~ expands properly
if [ $SOURCE_CONFIG_FILE_PATH="~" ]; then 
SOURCE_CONFIG_FILE_PATH=$HOME
fi

# Safeguard against no invoke script
if [ ! -f $INVOKE_SCRIPT ]; then
    fail "unable to locate: $INVOKE_SCRIPT"
fi

# Append to .rc file
echo "...Appending $INVOKE_SCRIPT to $SOURCE_CONFIG_FILE_PATH/$CONFIG_FILENAME"
echo "source $INVOKE_SCRIPT" >> $SOURCE_CONFIG_FILE_PATH/$CONFIG_FILENAME

# Run create_venv in same process
source create_venv.sh

# Enable invoke function
echo "...Activating"
source $SOURCE_CONFIG_FILE_PATH/$CONFIG_FILENAME