import subprocess
import os
from flask import Flask, send_from_directory, jsonify

# --- Git Update Logic ---
def update_repository():
    """
    Attempts to pull the latest changes from the git repository.
    Logs errors but does not let them halt application startup.
    """
    try:
        print("Attempting to pull latest changes from git...")
        # Using check=False to prevent raising CalledProcessError on non-zero exit
        # We will check the returncode manually.
        result = subprocess.run(
            ['git', 'pull'],
            capture_output=True,
            text=True,
            check=False # Important: do not raise exception on failure
        )
        if result.returncode == 0:
            print("Git pull successful.")
            if result.stdout:
                print("Git pull output:\n", result.stdout)
        else:
            # This is where "Command '['git', 'pull']' returned non-zero exit status 1." would be handled
            print(f"Git pull command failed with exit status {result.returncode}.")
            if result.stderr:
                print("Git pull error output:\n", result.stderr)
            # The application will continue running despite this failure.
    except FileNotFoundError:
        print("Git command not found. Make sure git is installed and in PATH. Skipping git pull.")
    except Exception as e:
        # Catch any other unexpected errors during git pull
        print(f"An unexpected error occurred during git pull: {str(e)}")

# --- Flask Application Setup ---
# Assumes your frontend build output is in a directory named 'build'.
# If it's different (e.g., 'dist', 'public'), change 'static_folder' accordingly.
app = Flask(__name__, static_folder='build', static_url_path='/')

@app.before_first_request
def initial_setup():
    """
    Perform initial setup tasks when the application starts,
    such as updating the repository.
    """
    print("Performing initial application setup...")
    update_repository()
    print("Initial setup complete. Application is ready.")

# --- Routes ---
@app.route('/')
def serve_index():
    """
    Serves the main index.html file from the static build folder.
    This is typically your frontend application.
    """
    # Check if index.html exists in the configured static_folder
    if not os.path.exists(os.path.join(app.static_folder, 'index.html')):
        # You can customize this response, e.g., return a more user-friendly error page
        return jsonify(error="index.html not found in static folder ('{}'). Make sure your frontend is built and placed correctly.".format(app.static_folder)), 404
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serves other static files from the build folder."""
    return send_from_directory(app.static_folder, path)

@app.route('/api/status', methods=['GET'])
def api_status():
    """
    A sample API endpoint to check backend status.
    """
    return jsonify(status="Backend is running", port=os.environ.get('PORT', '9000')), 200

# The following block is for running with `python app.py` (e.g., for local development).
# In production, Gunicorn (or another WSGI server) specified in startup.sh will be used.
if __name__ == '__main__':
    # Port is set via PORT environment variable in startup.sh or defaults to 9000
    configured_port = int(os.environ.get('PORT', 9000))
    print(f"Starting Flask development server on host 0.0.0.0, port {configured_port}...")
    # Note: For development, ensure your 'build' folder with 'index.html' exists or adjust paths.
    app.run(host='0.0.0.0', port=configured_port)
