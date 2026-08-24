import os

# Launcher for Render / production.
# The Flask application (routes, file handling) lives in resume.py.
# This file simply exposes it as the WSGI/entry point that
# `python app.py` (Render's start command) expects.

from resume import app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Render requires 0.0.0.0 so the service is reachable.
    app.run(host="0.0.0.0", port=port, debug=False)
