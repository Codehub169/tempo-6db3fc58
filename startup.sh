#!/bin/bash

# Ensure script exits immediately if a command exits with a non-zero status.
set -e

# Set the PORT environment variable strictly to 9000
export PORT=9000

echo "PORT is set to $PORT"

# (Optional) Navigate to the app directory if startup.sh is in the root
# Example: If your app.py is in /srv/app and startup.sh is in /srv
# cd /srv/app

# (Optional) Activate virtual environment if used
# if [ -d "venv" ]; then
#   echo "Activating virtual environment..."
#   source venv/bin/activate
# fi

# (Optional) Run database migrations or other pre-start tasks
# echo "Running database migrations (if any)..."
# flask db upgrade # Example for Flask-Migrate
# python manage.py migrate --noinput # Example for Django

# The Python app (app.py) already contains logic to attempt a git pull during its startup.

echo "Starting Gunicorn web server..."
# Replace 'app:app' with 'your_module:your_flask_app_instance' if your Python file
# is named differently or the Flask app object has a different name.
# --workers: Adjust based on your server's CPU cores. A common recommendation is (2 * CPU_CORES) + 1.
# --log-level: Set to 'info' or 'debug' for more verbose logging during startup/troubleshooting.
# --access-logfile - and --error-logfile - to log to stdout/stderr for container environments
exec gunicorn --bind 0.0.0.0:$PORT \
             --workers ${GUNICORN_WORKERS:-4} \
             --log-level ${GUNICORN_LOG_LEVEL:-info} \
             --access-logfile '-' \
             --error-logfile '-' \
             app:app
