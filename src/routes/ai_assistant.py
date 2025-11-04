from flask import Blueprint, jsonify, request
from src.middleware.keycloak_auth import require_auth
from src.services.ai_service import get_ai_assistant_feedback, generate_ai_rival

bp = Blueprint('ai_assistant', __name__)

@bp.route('/ai-assistant', methods=['POST'])
@require_auth
def ai_assistant():
    data = request.get_json()
    try:
        response_text = get_ai_assistant_feedback(
            code=data.get('code', ''),
            language=data.get('language', 'python'),
            exercise_name=data.get('exercise_name', ''),
            description=data.get('exercise_description', ''),
            reference_solution=data.get('reference_solution', '')
        )
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/ai-rival', methods=['POST'])
@require_auth
def ai_rival():
    data = request.get_json()
    try:
        response_text = generate_ai_rival(
            language=data.get('language', 'python'),
            exercise_name=data.get('exercise_name', ''),
            description=data.get('exercise_description', ''),
            difficulty=data.get('difficulty', 'easy')
        )
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
