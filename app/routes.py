from flask import Blueprint, jsonify, render_template, request

from app.logic import navigate

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html", outcome=navigate())


@bp.route("/directions", methods=["POST"])
def directions():
    return render_template("index.html", outcome=navigate(request.form))


@bp.route("/api/test")
def test():
    outcome = navigate({"entrance": "NPB_5_E1", "classroom": "NPB_5_154"})
    return jsonify(outcome)
