from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import and register routes
    from app import routes
    app.register_blueprint(routes.bp)
   #app.register_blueprint(routes.api_bp)  # ability to simply add more routes in the future

    return app