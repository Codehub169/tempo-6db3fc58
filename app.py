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
def update_repository() -> bool:
    """
    Attempts to pull the latest changes from the git repository.
    Logs errors and returns False on failure. Returns True on success.
    """
    try:
        _safe_print_stdout("Attempting to pull latest changes from git...")
        result = subprocess.run(
            ['git', 'pull'],
            capture_output=True,
            text=True,
            check=False, # Does not raise CalledProcessError on non-zero exit
            errors='replace',
            timeout=60  # Added timeout to prevent indefinite hanging
        )

        if result.returncode == 0:
            _safe_print_stdout("Git pull successful.")
            if result.stdout and result.stdout.strip():
                _safe_print_stdout(f"Git pull output:\n{result.stdout.strip()}")
            return True
        else:
            error_message = f"Git pull command failed with exit status {result.returncode}."
            _safe_print_stderr(error_message)
            if result.stderr and result.stderr.strip():
                _safe_print_stderr(f"Git pull error output (stderr):\n{result.stderr.strip()}")
            if result.stdout and result.stdout.strip(): # stdout might also contain useful info
                _safe_print_stderr(f"Git pull output (stdout on failure):\n{result.stdout.strip()}")
            return False

    except FileNotFoundError:
        _safe_print_stderr("Git command not found. Make sure git is installed and in PATH. Skipping git pull.")
        return False
    except subprocess.TimeoutExpired:
        _safe_print_stderr("Git pull command timed out after 60 seconds. Skipping git pull.")
        return False
    except Exception as e:
        _safe_print_stderr(f"An unexpected error occurred during git pull: {str(e)} ({type(e).__name__})")
        return False

# --- Flask Application Setup ---
app = Flask(__name__, static_folder='build', static_url_path='/')

def _perform_initial_setup() -> None:
    """
    Perform initial setup tasks, such as attempting to update the repository.
    If repository update fails, it logs an error and continues running with the current code.
    Other critical setup errors will still cause the application to exit.
    """
    try:
        _safe_print_stdout("Performing initial application setup...")
        if not update_repository():
            _safe_print_stderr("WARNING: Failed to update repository during initial setup. See logs above for details.")
            _safe_print_stderr("Application will continue with the current version of the code. Manual intervention may be required to update.")
            # sys.exit(1) # Removed: Application will continue running
        else:
            _safe_print_stdout("Repository update successful.")
        _safe_print_stdout("Initial setup tasks finished. Application is ready to start.")
    except Exception as e:
        _safe_print_stderr(f"CRITICAL UNHANDLED ERROR during initial application setup: {str(e)} ({type(e).__name__})")
        _safe_print_stderr("Application will not start due to an unexpected critical error.")
        sys.exit(1) # Exit for other critical setup errors

# --- Routes ---
@app.route('/')
def serve_index() -> Union[Response, Tuple[Response, int]]:
    """Serves the main index.html file from the static folder."""
    index_path = os.path.join(app.static_folder, 'index.html')
    if not os.path.isfile(index_path):
        _safe_print_stderr(f"Error: index.html not found at {index_path}. Ensure frontend is built into '{app.static_folder}'.")
        return jsonify(error="Application frontend not found. Please contact support."), 404
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path: str) -> Response:
    """Serves other static files (CSS, JS, images) from the static folder."""
    return send_from_directory(app.static_folder, path)

@app.route('/api/status', methods=['GET'])
def api_status() -> Tuple[Response, int]:
    """API endpoint to check backend status and configured port."""
    # Reads PORT from env, which should be set to 9000 by app main block
    port_str = os.environ.get('PORT', '9000') 
    return jsonify(status="Backend is running", configured_port=port_str), 200

# --- Main Execution Block ---
if __name__ == '__main__':
    _perform_initial_setup() # Perform git pull and other setup tasks.

    # Strictly configure port to 9000
    configured_port = 9000
    # Set PORT in environment so api_status and other potential readers see the correct port
    os.environ['PORT'] = str(configured_port) 
    _safe_print_stdout(f"Application strictly configured to run on port {configured_port}.")
    
    _safe_print_stdout(f"Starting Flask application server on host 0.0.0.0, port {configured_port}...")
    app.run(host='0.0.0.0', port=configured_port, debug=False)
