# run.py
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Run with: uv run run.py
    debug = os.getenv("FLASK_DEBUG", "0") in ("1", "true", "True")
    app.run(debug=debug)