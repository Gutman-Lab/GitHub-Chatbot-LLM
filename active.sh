#!/bin/bash

# Go to backend directory
cd /nashome/bhavesh/react-llm-github/backend/ || exit 1

# Activate virtual environment
source .venv/bin/activate

export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH


cd /nashome/bhavesh/react-llm-github
