from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from database.db import get_db
from middleware.keycloak_auth import require_auth
from services.exercise_service import (
    get_all_exercises,
    get_exercise_by_id,
    create_exercise,
    update_exercise,
    delete_exercise
)

bp = Blueprint('exercises', __name__)

@bp.route('/exercises', methods=['GET'])
@require_auth
def get_exercises_route():
    db: Session = get_db()
    exercises = get_all_exercises(db)
    return jsonify(exercises)

@bp.route('/exercises/<int:exercise_id>', methods=['GET'])
@require_auth
def get_exercise_route(exercise_id):
    db: Session = get_db()
    exercise = get_exercise_by_id(db, exercise_id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404
    return jsonify(exercise)

@bp.route('/exercises', methods=['POST'])
@require_auth
def create_exercise_route():
    db: Session = get_db()
    data = request.get_json()
    try:
        new_exercise = create_exercise(db, data)
        return jsonify(new_exercise), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/exercises/<int:exercise_id>', methods=['PUT'])
@require_auth
def update_exercise_route(exercise_id):
    db: Session = get_db()
    data = request.get_json()
    try:
        updated_exercise = update_exercise(db, exercise_id, data)
        if not updated_exercise:
            return jsonify({"error": "Exercise not found"}), 404
        return jsonify(updated_exercise)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/exercises/<int:exercise_id>', methods=['DELETE'])
@require_auth
def delete_exercise_route(exercise_id):
    db: Session = get_db()
    try:
        success = delete_exercise(db, exercise_id)
        if not success:
            return jsonify({"error": "Exercise not found"}), 404
        return jsonify({"message": "Exercise deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
