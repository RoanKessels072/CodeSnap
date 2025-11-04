from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from src.database.db import get_db_session
from src.services.attempt_service import create_attempt
from src.services.user_service import get_or_create_user
from src.middleware.keycloak_auth import require_auth
from src.services.user_service import get_user_by_keycloak_id
from src.models.attempt import Attempt

bp = Blueprint("attempts", __name__)

@bp.route("/", methods=["POST"])
@require_auth
def submit_attempt():
    data = request.get_json()
    user_info = request.user_info

    if not data or "exerciseId" not in data or "code" not in data:
        return jsonify({"error": "Missing 'exerciseId' or 'code'"}), 400

    exercise_id = data["exerciseId"]
    code = data["code"]

    db: Session = get_db_session()
    try:
        user = get_or_create_user(
            db,
            keycloak_id=user_info['keycloak_id'],
            email=user_info['email'],
            username=user_info['username']
        )

        attempt = create_attempt(db, user.id, exercise_id, code)

        response_data = {
            "attempt_id": attempt.id,
            "stars": attempt.stars,
            "score": attempt.score,
            "user_id": user.id,
            "exercise_id": attempt.exercise_id
        }

    except ValueError as e:
        print(f"ValueError: {e}", flush=True)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal error: {str(e)}"}), 500
    finally:
        db.close()

    return jsonify(response_data)

@bp.route("/user", methods=["GET"])
@require_auth
def get_user_attempts():
    """Get all attempts for the authenticated user"""
    user_info = request.user_info
    db: Session = get_db_session()
    
    try:    
        user = get_user_by_keycloak_id(db, user_info['keycloak_id'])
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        attempts = db.query(Attempt).filter(Attempt.user_id == user.id).all()
        
        result = []
        for attempt in attempts:
            result.append({
                'id': attempt.id,
                'exercise_id': attempt.exercise_id,
                'score': attempt.score,
                'stars': attempt.stars,
                'attempted_at': attempt.attempted_at.isoformat()
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()