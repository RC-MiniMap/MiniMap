from flask import Blueprint, render_template, jsonify, request
from app.logic import get_directions, get_options, get_floor_bounds

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    entrances, classrooms = get_options()
    return render_template('index.html', entranceOptions=entrances, classroomOptions=classrooms)

@bp.route('/directions', methods=['POST'])
def directions():
    steps = None
    coordinates = None
    floor_bounds = None
    error = None
    entrance = request.form.get('entrance')
    classroom = request.form.get('classroom')
    if not entrance or not classroom:
        error = 'Missing entrance or classroom parameter'
    else:
        try:
            result = get_directions(entrance, classroom)
            if isinstance(result, str):
                error = 'No route could be found between the selected entrance and destination. Please check your selections and try again.'
            else:
                steps = result["directions"]
                coordinates = result["coordinates"]
                if coordinates:
                    building = entrance.split('_')[0]
                    floor = coordinates[0]["floor"]
                    floor_bounds = get_floor_bounds(building, floor)
        except RuntimeError as e:
            error = str(e)
    entrances, classrooms = get_options()
    return render_template('index.html', steps=steps, coordinates=coordinates, floor_bounds=floor_bounds,
                           error=error, entranceOptions=entrances, classroomOptions=classrooms)

@bp.route('/api/test')
def test():
    directions = get_directions("NPB_5_E1", "NPB_5_154")
    return jsonify(directions)
