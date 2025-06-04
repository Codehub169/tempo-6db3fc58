#!/bin/sh
# This script starts the Python application.

# Exit immediately if a command exits with a non-zero status.
set -e

# It's good practice to ensure the script is run from the application's root directory
# or that app.py is found in Python's path or via a relative/absolute path.
# For simplicity, this assumes app.py is in the same directory as startup.sh or in PYTHONPATH.

_safe_print_stdout "Starting application via startup.sh..."

# Run the Python application.
# The Python application (app.py) is configured to handle port settings (strictly 9000)
# and other necessary configurations internally.
python3 app.py

_safe_print_stdout "Application startup script finished."
