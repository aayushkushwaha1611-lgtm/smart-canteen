"""Smart Canteen - application entry point.

Usage:
    python run.py
"""
import os

from app import create_app
from config import get_config

app = create_app(get_config(os.environ.get("FLASK_ENV")))

if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
