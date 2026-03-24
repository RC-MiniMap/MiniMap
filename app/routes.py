from flask import Blueprint, render_template, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Render the main search + map page
    return render_template('index.html')

@bp.route('/api/test')
def test():
    # Test route — confirms the API layer is connected
    return jsonify({'status': 'ok', 'message': 'Campus Navigator API is live'})