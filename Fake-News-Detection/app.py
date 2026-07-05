"""
app.py
------
Main Flask application entry point for the AI Fake News Detection system.
Fully offline - no external APIs or cloud services are used anywhere.

Run:
    python app.py

Then open http://127.0.0.1:5000 in your browser.
"""

import os
from flask import Flask

from routes.main_routes import main_bp
from routes.dashboard_routes import dash_bp
from routes.report_routes import report_bp
from database.init_db import init_db


def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret-key-change-in-production"
    app.config["JSON_SORT_KEYS"] = False

    # Ensure DB exists
    init_db()

    app.register_blueprint(main_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(report_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
