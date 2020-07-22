#!/bin/bash

echo "Creating a new virtual environment..."
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
