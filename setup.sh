#!/bin/bash

# Upgrade pip to the latest version
pip install --upgrade pip

# Install all Python dependencies
pip install -r requirements.txt

# Optional: echo success
echo "Setup completed successfully!"
chmod +x setup.sh
