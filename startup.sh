#!/bin/bash
# This script starts the Python application on port 9000.

# Exit immediately if a command exits with a non-zero status.
set -e

# Ensure this script has execute permissions: chmod +x startup.sh

# Set the port for the application.
# The Python application (app.py) should be configured to read this PORT variable.
export PORT=9000
echo "PORT is set to $PORT"

# Navigate to the directory where app.py is located, if necessary.
# This ensures that relative paths for static files (e.g., 'build' folder)
# and module imports work as expected.
# Example: If your app.py is in /srv/app and this script is in /srv:
# cd "$(dirname "$0")/app" # Navigate to 'app' subdirectory relative to script
# Or simply: cd /srv/app

echo "Starting Python application on port $PORT..."

# (Optional) Activate virtual environment if used
# Make sure the path to your virtual environment is correct.
# if [ -d "venv" ]; then
#   echo "Activating virtual environment..."
#   source venv/bin/activate
# elif [ -d ".venv" ]; then
#   echo "Activating virtual environment (.venv)..."
#   source .venv/bin/activate
# fi

# Run the Python application using 'exec'.
# 'exec' replaces the shell process with the Python process, which is good practice
# for process management and signal handling, especially in containerized environments.
# Replace 'app.py' with the actual name of your main Python file if it's different.
# Note: Using Flask's built-in development server (via python app.py) is not recommended for production.
# For production, a WSGI server like Gunicorn should be used.
exec python app.py
