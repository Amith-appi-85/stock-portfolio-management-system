"""
run.py
--------
Entry point to run the Flask development server.

Usage:
    python run.py

For production, use gunicorn instead (see docs/deployment.md):
    gunicorn -w 4 -b 0.0.0.0:8000 run:app
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
