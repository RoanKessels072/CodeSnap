from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from database.db import get_db_session
from services.attempt_service import create_attempt

bp = Blueprint("attempts", __name__)

@bp.route("/", methods=["POST"])
def submit_attempt():
    print("=== Received request ===")
    data = request.get_json()
    print(f"Data: {data}")
    
    if not data or "exerciseId" not in data or "code" not in data:
        return jsonify({"error": "Missing 'exercise_Id' or 'code'"}), 400

    exercise_id = data["exerciseId"]
    code = data["code"]
    user_id = 1
    
    print(f"Exercise ID: {exercise_id}, User ID: {user_id}")

    db: Session = get_db_session()
    print("Got database session")

    try:
        print("Calling create_attempt...")
        attempt = create_attempt(db, user_id, exercise_id, code)
        print(f"Attempt created: {attempt.id}")
    except ValueError as e:
        print(f"ValueError: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

    return jsonify({
        "attempt_id": attempt.id,
        "stars": attempt.stars,
        "style_score": attempt.style_score,
        "test_pass_rate": attempt.test_pass_rate,
        "feedback": attempt.feedback
    })