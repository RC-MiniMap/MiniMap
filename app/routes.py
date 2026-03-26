from flask import Blueprint, render_template, jsonify, request
from app.logic import get_directions

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/directions', methods=['POST'])
def directions():
    steps = None
    coordinates = None
    error = None
    entrance = request.form.get('entrance')
    classroom = request.form.get('classroom')
    if not entrance or not classroom:
        error = 'Missing entrance or classroom parameter'
    else:
        result = get_directions(entrance, classroom)
        if result == "No path found":
            error = 'No path found'
        else:
            steps, coordinates = result
    return render_template('index.html', steps=steps, coordinates=coordinates, error=error)

@bp.route('/api/test')
def test():
    directions = get_directions("room_101", "room_102")
    return jsonify(directions)
