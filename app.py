import subprocess
import os
import sys # Added for sys.stderr
from flask import Flask, send_from_directory, jsonify, Response
from typing import Tuple, Union

# --- Git Update Logic ---
def update_repository() -> None:
    """
    Attempts to pull the latest changes from the git repository.
    Logs errors robustly but does not let them halt application startup.
    """
    try:
        print("Attempting to pull latest changes from git...")
        # Using check=False to prevent raising CalledProcessError on non-zero exit.
        # errors='replace' handles potential undecodable characters in git output.
        result = subprocess.run(
            ['git', 'pull'],
            capture_output=True,
            text=True,
            check=False, # Important: do not raise exception on git command failure
            errors='replace' # Handle non-UTF8 characters in output
        )
        if result.returncode == 0:
            try:
                print("Git pull successful.")
                if result.stdout:
                    print(f"Git pull output:\n{result.stdout}")
            except Exception:
                # If logging success fails, ignore to ensure app continues
                pass
        else:
            try:
                # Log failure to stderr
                error_message = f"Git pull command failed with exit status {result.returncode}."
                print(error_message, file=sys.stderr)
                if result.stderr:
                    print(f"Git pull error output (stderr):\n{result.stderr}", file=sys.stderr)
                # It can be useful to see stdout as well, even on failure.
                if result.stdout:
                    print(f"Git pull output (stdout on failure):\n{result.stdout}", file=sys.stderr)
            except Exception:
                # If logging failure details fails, ignore
                pass
            # The application will continue running despite this failure.
    except FileNotFoundError:
        try:
            print("Git command not found. Make sure git is installed and in PATH. Skipping git pull.", file=sys.stderr)
        except Exception:
            pass # If logging this fails, ignore
    except Exception as e:
        try:
            # Catch any other unexpected errors during git pull attempt
            print(f"An unexpected error occurred during git pull: {str(e)}", file=sys.stderr)
        except Exception:
            pass # If logging this fails, ignore

# --- Flask Application Setup ---
# Assumes your frontend build output is in a directory named 'build'.
# If it's different (e.g., 'dist', 'public'), change 'static_folder' accordingly.
app = Flask(__name__, static_folder='build', static_url_path='/')

def _perform_initial_setup() -> None:
    """
    Perform initial setup tasks when the application module is loaded,
    such as updating the repository. Catches and logs unexpected errors.
    """
    try:
        print("Performing initial application setup...")
        update_repository()
        print("Initial setup complete. Application is ready.")
    except Exception as e:
        try:
            # Use sys.stderr for critical startup errors
            print(f"CRITICAL ERROR during initial application setup: {str(e)}", file=sys.stderr)
            print("Application may not function correctly or fully as expected.", file=sys.stderr)
        except Exception:
            # If logging critical error itself fails, there's not much more to do here
            pass

_perform_initial_setup()

# --- Routes ---
@app.route('/')
def serve_index() -> Union[Response, Tuple[Response, int]]:
    """
    Serves the main index.html file from the static build folder.
    This is typically your frontend application.
    """
    index_path = os.path.join(app.static_folder, 'index.html')
    if not os.path.exists(index_path):
        return jsonify(error=f"index.html not found in static folder ('{app.static_folder}'). Make sure your frontend is built and placed correctly."), 404
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path: str) -> Response:
    """Serves other static files from the build folder."""
    return send_from_directory(app.static_folder, path)

@app.route('/api/status', methods=['GET'])
def api_status() -> Tuple[Response, int]:
    """
    A sample API endpoint to check backend status.
    """
    # PORT will be set by startup.sh, default to '9000' if somehow not set.
    port_str = os.environ.get('PORT', '9000') 
    return jsonify(status="Backend is running", port=port_str), 200

if __name__ == '__main__':
    # For local development, strictly use port 9000
    configured_port = 9000
    
    print(f"Starting Flask development server on host 0.0.0.0, port {configured_port}...")
    app.run(host='0.0.0.0', port=configured_port)
