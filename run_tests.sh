#!/bin/bash

# Azure Speech Service Test Runner
# This script sets up the environment and runs the Azure Speech tests

set -e

echo "Azure Speech Service Test Runner"
echo "================================"

# Check if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "No .env file found. Using system environment variables."
    echo "You can create a .env file from .env.example for easier configuration."
fi

# Check if required environment variables are set
if [ -z "$AZURE_SPEECH_KEY" ]; then
    echo "Error: AZURE_SPEECH_KEY environment variable is not set"
    echo "Please set it in your .env file or as an environment variable"
    exit 1
fi

if [ -z "$AZURE_SPEECH_REGION" ] && [ -z "$AZURE_SPEECH_ENDPOINT" ]; then
    echo "Error: Either AZURE_SPEECH_REGION or AZURE_SPEECH_ENDPOINT must be set"
    echo "Please set one of them in your .env file or as environment variables"
    exit 1
fi

# Install requirements if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Check if virtual environment activation script exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Virtual environment activation script not found"
    echo "Trying to recreate virtual environment..."
    rm -rf venv
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

echo "Activating virtual environment..."
if source venv/bin/activate; then
    echo "Virtual environment activated successfully"
    echo "Installing/updating requirements..."
    pip install -r requirements.txt
else
    echo "Warning: Failed to activate virtual environment"
    echo "Falling back to system Python..."
    echo "Installing requirements with user flag..."
    pip3 install --user -r requirements.txt
fi

echo ""
echo "Running Azure Speech Service tests..."
echo "====================================="
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Using virtual environment: $VIRTUAL_ENV"
    python azure_speech_test.py
else
    echo "Using system Python"
    python3 azure_speech_test.py
fi

echo ""
echo "Test completed!"
