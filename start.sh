#!/bin/bash

# Define the virtual environment name
VENV_NAME="smolagent"

# Check if the virtual environment exists
if [ ! -d "$VENV_NAME" ]; then
    echo "Virtual environment '$VENV_NAME' not found. Creating it..."
    python3 -m venv "$VENV_NAME"
    echo "Virtual environment '$VENV_NAME' created."
fi

# Activate the virtual environment
source "$VENV_NAME/bin/activate"

# Check if requirements.txt exists and install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    echo "Dependencies installed."
else
    echo "requirements.txt not found. Skipping dependency installation."
fi

echo "Virtual environment '$VENV_NAME' is ready and activated."

python client_chat_w_history.py
# Deactivate the virtual environment  
deactivate