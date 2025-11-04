from flask import Blueprint, jsonify, request
from database.db import get_db_session
from middleware.keycloak_auth import require_auth
from services.user_service import (
    get_all_users,
    get_user_by_id,
    update_user_preference,
    delete_user,
    sync_user_from_keycloak
)

bp = Blueprint('users', __name__)

@bp.route('/', methods=['GET'])
@require_auth
def list_users():
    db = get_db_session()
    try:
        users = get_all_users(db)
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    db = get_db_session()
    try:
        user_info = request.user_info
        user = sync_user_from_keycloak(
            db,
            keycloak_id=user_info['keycloak_id'],
            username=user_info.get('username'),
            email=user_info.get('email')
        )

        return jsonify({
            "id": user.id,
            "keycloak_id": user.keycloak_id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/me', methods=['PUT'])
@require_auth
def update_current_user():
    db = get_db_session()
    try:
        user_info = request.user_info
        data = request.get_json()

        user = update_user_preference(db, keycloak_id=user_info['keycloak_id'], data=data)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            "id": user.id,
            "keycloak_id": user.keycloak_id,
            "username": user.username,
            "email": user.email,
            "preferred_language": user.preferred_language,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:user_id>', methods=['GET'])
@require_auth
def get_user_by_id_route(user_id):
    db = get_db_session()
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/<keycloak_id>', methods=['DELETE'])
@require_auth
def delete_user_route(keycloak_id):
    db = get_db_session()
    try:
        success = delete_user(db, keycloak_id)
        if not success:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
