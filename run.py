# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run with: uv run run.py
    app.run(debug=True)