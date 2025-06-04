#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error when substituting.
set -u

# Determine the script's directory and change to it.
# This ensures that relative paths (like for app.py) work correctly
# and that the application context is as expected.
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

# Set the port for the application.
# Uses the PORT environment variable if it's already set, otherwise defaults to 9000.
export PORT=${PORT:-9000}

echo "Starting application on port $PORT..."

# Run the Python application using exec to replace the shell process.
# This is more efficient as it avoids leaving an unnecessary shell process running.
# Ensure 'python' (or 'python3') points to your desired Python interpreter.
exec python app.py
