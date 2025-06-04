#!/bin/sh

# Set the port for the application
export PORT=9000

# Navigate to the directory where app.py is located, if necessary.
# For example, if your app is in /opt/app:
# cd /opt/app

echo "Starting application on port $PORT..."
# Run the Python application.
# Ensure 'python' points to a Python 3 interpreter or use 'python3'.
python app.py
