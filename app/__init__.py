from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import and register routes
    from app import routes
    app.register_blueprint(routes.bp)
    # To add additional blueprints (e.g., api_bp), register them here.

    return app