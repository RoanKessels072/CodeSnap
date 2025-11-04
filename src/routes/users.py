from flask import Blueprint, jsonify, request
from database.db import get_db_session
from models.user import User
from middleware.keycloak_auth import require_auth

bp = Blueprint('users', __name__)

@bp.route('/', methods=['GET'])
@require_auth
def get_users():
    db = get_db_session()
    try:
        users = db.query(User).all()
        
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'keycloak_id': user.keycloak_id,
                'username': user.username,
                'preferred_language': user.preferred_language,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == request.user.id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'keycloak_id': user.keycloak_id,
            'username': user.username,
            'preferred_language': user.preferred_language,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'keycloak_id': user.keycloak_id,
            'username': user.username,
            'preferred_language': user.preferred_language,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
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
        user = db.query(User).filter(User.id == request.user.id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'preferred_language' in data:
            user.preferred_language = data['preferred_language']
        
        db.commit()
        db.refresh(user)
        
        return jsonify({
            'id': user.id,
            'keycloak_id': user.keycloak_id,
            'username': user.username,
            'preferred_language': user.preferred_language,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.delete(user)
        db.commit()
        
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()