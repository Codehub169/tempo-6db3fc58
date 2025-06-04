#!/usr/bin/env python3

import subprocess
import os
import sys
from flask import Flask, send_from_directory, jsonify, Response
from typing import Tuple, Union

# --- Helper functions for safe printing ---
def _safe_print_to_stream(stream, *args, **kwargs) -> None:
    """Safely prints to the given stream, ignoring errors during printing itself."""
    try:
        print(*args, file=stream, **kwargs)
        stream.flush() # Ensure it's written, esp. if daemonized or output redirected
    except Exception:
        pass # Cannot do much if the stream itself is broken

def _safe_print_stdout(*args, **kwargs) -> None:
    """Safely prints to sys.stdout."""
    _safe_print_to_stream(sys.stdout, *args, **kwargs)

def _safe_print_stderr(*args, **kwargs) -> None:
    """Safely prints to sys.stderr."""
    _safe_print_to_stream(sys.stderr, *args, **kwargs)


# --- Git Update Logic ---
def update_repository() -> None:
    """
    Attempts to pull the latest changes from the git repository.
    Logs errors robustly but does not let them halt application startup.
    """
    try:
        _safe_print_stdout("Attempting to pull latest changes from git...")
        # Assuming the script is run from the repository root or startup.sh handles CWD.
        result = subprocess.run(
            ['git', 'pull'],
            capture_output=True,
            text=True,        # Decodes stdout/stderr as text (UTF-8 by default)
            check=False,      # Do not raise CalledProcessError on non-zero exit
            errors='replace'  # Replace non-decodable characters in output
        )

        if result.returncode == 0:
            _safe_print_stdout("Git pull successful.")
            # Log stdout only if it contains meaningful content
            if result.stdout and result.stdout.strip():
                _safe_print_stdout(f"Git pull output:\n{result.stdout.strip()}")
        else:
            error_message = f"Git pull command failed with exit status {result.returncode}."
            _safe_print_stderr(error_message)
            if result.stderr and result.stderr.strip():
                _safe_print_stderr(f"Git pull error output (stderr):\n{result.stderr.strip()}")
            # stdout might also contain useful info on failure (e.g. merge conflicts)
            if result.stdout and result.stdout.strip():
                _safe_print_stderr(f"Git pull output (stdout on failure):\n{result.stdout.strip()}")
            _safe_print_stderr("Application will start with the existing codebase.")

    except FileNotFoundError:
        _safe_print_stderr("Git command not found. Make sure git is installed and in PATH. Skipping git pull.")
    except Exception as e:
        # Catch any other unexpected errors during the git pull process
        _safe_print_stderr(f"An unexpected error occurred during git pull: {str(e)} ({type(e).__name__})")

# --- Flask Application Setup ---
# static_folder='build' serves files from the 'build' directory.
# static_url_path='/' makes these files accessible from the root URL (e.g., /index.html).
app = Flask(__name__, static_folder='build', static_url_path='/')

def _perform_initial_setup() -> None:
    """
    Perform initial setup tasks, such as updating the repository.
    This function is called when the script is run directly.
    """
    try:
        _safe_print_stdout("Performing initial application setup...")
        update_repository()
        _safe_print_stdout("Initial setup complete. Application is ready to start.")
    except Exception as e:
        _safe_print_stderr(f"CRITICAL ERROR during initial application setup: {str(e)} ({type(e).__name__})")
        _safe_print_stderr("Application may not function correctly or fully as expected.")

# --- Routes ---
@app.route('/')
def serve_index() -> Union[Response, Tuple[Response, int]]:
    """Serves the main index.html file from the static folder."""
    # app.static_folder is an absolute path once the app is configured.
    index_path = os.path.join(app.static_folder, 'index.html')
    if not os.path.isfile(index_path):
        # Log server-side for easier debugging by developers
        _safe_print_stderr(f"Error: index.html not found at {index_path}. Ensure frontend is built into '{app.static_folder}'.")
        # User-facing error
        return jsonify(error="Application frontend not found. Please contact support."), 404
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path: str) -> Response:
    """Serves other static files (CSS, JS, images) from the static folder."""
    return send_from_directory(app.static_folder, path)

@app.route('/api/status', methods=['GET'])
def api_status() -> Tuple[Response, int]:
    """API endpoint to check backend status and configured port."""
    # Report the port the application was configured to attempt to use.
    port_str = os.environ.get('PORT', '9000') 
    return jsonify(status="Backend is running", configured_port=port_str), 200

# --- Main Execution Block ---
if __name__ == '__main__':
    _perform_initial_setup() # Perform git pull and other setup tasks

    default_port = 9000
    try:
        # Read port from environment variable, default to 9000 if not set or invalid
        port_env_value = os.environ.get('PORT')
        if port_env_value is None:
            configured_port = default_port
            _safe_print_stdout(f"PORT environment variable not set. Defaulting to {default_port}.")
        else:
            configured_port = int(port_env_value)
    except ValueError:
        _safe_print_stderr(f"Warning: Invalid PORT value '{port_env_value}'. Defaulting to {default_port}.")
        configured_port = default_port
    
    _safe_print_stdout(f"Starting Flask application server on host 0.0.0.0, port {configured_port}...")
    # app.run() is suitable for development. For production, use a WSGI server like Gunicorn.
    # debug=False is a safer default for production/staging environments.
    app.run(host='0.0.0.0', port=configured_port, debug=False)
