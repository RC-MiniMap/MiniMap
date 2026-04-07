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
        try:
            result = get_directions(entrance, classroom)
            if result == "No path found":
                error = 'No route could be found between the selected entrance and destination. Please check your selections and try again.'
            else:
                steps, coordinates = result
        except RuntimeError as e:
            error = str(e)
    return render_template('index.html', steps=steps, coordinates=coordinates, error=error)

@bp.route('/api/test')
def test():
    directions = get_directions("NPB_5_E1", "NPB_5_102")
    return jsonify(directions)
