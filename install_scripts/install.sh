#!/bin/bash

# Set bashrc or zshrc
echo "Choose install directory: bashrc - 1, zshrc - 2" 
read -p "Enter: " CONFIG

if [ "$CONFIG" -eq 1 ]; then
    CONFIG_FILENAME=".bashrc"
elif [ "$CONFIG" -eq 2 ]; then
    CONFIG_FILENAME=".zshrc"
else
    echo "Exiting..."
    exit
fi

echo "Installing invocation script to $CONFIG_FILENAME"

SOURCE_CONFIG_FILE_PATH="~"
CURRENT_DIR=$(pwd)

# Invoke from parent directory
INVOKE_SCRIPT="$(dirname "$CURRENT_DIR")/invoke_gpt.sh"

# Ensure ~ expands properly
if [ $SOURCE_CONFIG_FILE_PATH = "~" ]; then 
    SOURCE_CONFIG_FILE_PATH=$HOME
fi

# Safeguard against no invoke script
if [ ! -f $INVOKE_SCRIPT ]; then
    fail "unable to locate: $INVOKE_SCRIPT"
fi

# Append to .rc file
echo "Appending reference to invoke_gpt.sh in $SOURCE_CONFIG_FILE_PATH/$CONFIG_FILENAME"
echo "source $INVOKE_SCRIPT" "$(dirname $INVOKE_SCRIPT)" >> $SOURCE_CONFIG_FILE_PATH/$CONFIG_FILENAME

# Run create_venv in same process
source create_venv.sh

# Enable invoke function
echo "...Activating"
if [ "$CONFIG_FILENAME" = ".zshrc" ]; then
    zsh
fi

echo "Reading $CONFIG_FILENAME from $SOURCE_CONFIG_FILE_PATH"

source "$SOURCE_CONFIG_FILE_PATH/$CONFIG_FILENAME"

