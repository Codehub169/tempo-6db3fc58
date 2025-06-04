#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting up the application..."

# Set the port for the application
export PORT=9000
echo "Application will run on port $PORT"

# (Optional) Add any build steps here if needed, e.g., for a frontend
# echo "Running frontend build..."
# Example: npm install --prefix ./frontend && npm run build --prefix ./frontend
# (Ensure the output directory matches Flask's static_folder, e.g., copy to './build')

# Navigate to the application directory if startup.sh is not at the root
# cd /path/to/your/app

# Run the Python backend application using Gunicorn
# Assumes your Flask app object is named 'app' in a file named 'app.py'
# Gunicorn is a production-ready WSGI server.
# Ensure Gunicorn is installed in your environment (e.g., in requirements.txt or installed globally)
echo "Launching Gunicorn server for app:app on 0.0.0.0:$PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --log-level info app:app

# Alternative for Flask's development server (not for production):
# echo "Launching Flask development server..."
# exec python app.py

# Alternative for FastAPI with Uvicorn:
# echo "Launching Uvicorn server for app:app on 0.0.0.0:$PORT..."
# exec uvicorn app:app --host 0.0.0.0 --port $PORT --workers 4 --log-level info
