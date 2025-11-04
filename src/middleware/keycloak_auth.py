from functools import wraps
from flask import request, jsonify
import jwt
from jwt import PyJWKClient
import os
from database.db import get_db_session
from models.user import User
from datetime import datetime, timezone

KEYCLOAK_URL = os.getenv('KEYCLOAK_URL', 'http://localhost:8080')
KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', 'codesnap')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', 'codesnap-client')

_jwks_client = None

def get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client

def verify_token(token):
    try:
        print("=== TOKEN VERIFICATION ===")
        print(f"Getting JWKS client...")
        jwks_client = get_jwks_client()
        
        print(f"Getting signing key...")
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        print(f"Decoding token...")
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True, "verify_aud": False}
        )
        
        print(f"Token decoded successfully")
        print(f"Subject: {decoded.get('sub')}")
        print(f"Username: {decoded.get('preferred_username')}")
        print(f"Audience: {decoded.get('aud')}")
        
        token_audience = decoded.get('aud', [])
        if isinstance(token_audience, str):
            token_audience = [token_audience]
        
        valid_audiences = [KEYCLOAK_CLIENT_ID, 'account']
        print(f"Valid audiences: {valid_audiences}")
        print(f"Token audiences: {token_audience}")
        
        if not any(aud in valid_audiences for aud in token_audience):
            raise ValueError(f"Invalid audience. Expected one of {valid_audiences}, got {token_audience}")
        
        print(f"Audience verified successfully")
        print("=== VERIFICATION SUCCESS ===")
        return decoded
    except jwt.ExpiredSignatureError:
        print("ERROR: Token has expired")
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        print(f"ERROR: Invalid token - {str(e)}")
        raise ValueError(f"Invalid token: {str(e)}")
    except Exception as e:
        print(f"ERROR: Token verification failed - {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Token verification failed: {str(e)}")

def sync_user_from_token(decoded_token):
    db = get_db_session()
    try:
        keycloak_id = decoded_token.get('sub')
        username = decoded_token.get('preferred_username')
        
        if not keycloak_id:
            raise ValueError("Token missing 'sub' claim")
        
        user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
        
        if not user:
            print(f"Creating new user with keycloak_id: {keycloak_id}")
            user = User(
                keycloak_id=keycloak_id,
                username=username,
                last_login=datetime.now(timezone.utc)
            )
            db.add(user)
        else:
            print(f"Updating existing user: {user.id}")
            user.last_login = datetime.now(timezone.utc)
            if username and user.username != username:
                user.username = username
        
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        print(f"Error syncing user: {str(e)}")
        raise
    finally:
        db.close()

def get_user_info_from_token(decoded_token, user):
    return {
        'id': user.id,
        'keycloak_id': decoded_token.get('sub'),
        'email': decoded_token.get('email'),
        'username': decoded_token.get('preferred_username'),
        'name': decoded_token.get('name'),
        'roles': decoded_token.get('realm_access', {}).get('roles', []),
    }

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        print("=== AUTH DEBUG ===")
        print(f"Auth header present: {auth_header is not None}")
        
        if not auth_header:
            print("ERROR: No authorization header")
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            print(f"Token extracted (first 20 chars): {token[:20]}...")
            
            decoded_token = verify_token(token)
            print(f"Token verified successfully for user: {decoded_token.get('preferred_username')}")
            
            user = sync_user_from_token(decoded_token)
            print(f"User synced: ID={user.id}, username={user.username}")
            
            user_info = get_user_info_from_token(decoded_token, user)
            print(f"User info: {user_info}")
            
            request.user_info = user_info
            request.user = user
            
            return f(*args, **kwargs)
        except ValueError as e:
            print(f"ValueError during auth: {str(e)}")
            return jsonify({'error': str(e)}), 401
        except Exception as e:
            print(f"Exception during auth: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
    
    return decorated_function

def optional_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
                decoded_token = verify_token(token)
                user = sync_user_from_token(decoded_token)
                user_info = get_user_info_from_token(decoded_token, user)
                request.user_info = user_info
                request.user = user
            except:
                request.user_info = None
                request.user = None
        else:
            request.user_info = None
            request.user = None
        
        return f(*args, **kwargs)
    
    return decorated_function