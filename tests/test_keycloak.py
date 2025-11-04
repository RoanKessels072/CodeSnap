import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify, request
import jwt
from src.middleware.keycloak_auth import (
    get_jwks_client,
    verify_token,
    sync_user_from_token,
    get_user_info_from_token,
    require_auth,
    optional_auth
)
from src.models.user import User

@pytest.fixture
def flask_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    @app.route('/protected')
    @require_auth
    def protected():
        return jsonify({'user': request.user_info['username']})
    
    @app.route('/optional')
    @optional_auth
    def optional():
        if request.user_info:
            return jsonify({'user': request.user_info['username']})
        return jsonify({'user': 'anonymous'})
    
    return app

class TestKeycloakAuth:
    def test_get_jwks_client_singleton(self):
        with patch('middleware.keycloak_auth.PyJWKClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            
            import src.middleware.keycloak_auth
            src.middleware.keycloak_auth._jwks_client = None
            
            client1 = get_jwks_client()
            client2 = get_jwks_client()
            
            assert client1 is client2
            mock_client.assert_called_once()

    @patch('middleware.keycloak_auth.get_jwks_client')
    @patch('jwt.decode')
    def test_verify_token_success(self, mock_decode, mock_get_client):
        mock_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test_key"
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_get_client.return_value = mock_client
        
        mock_decode.return_value = {
            'sub': 'user-123',
            'preferred_username': 'testuser',
            'aud': ['codesnap-client']
        }
        
        result = verify_token("fake.jwt.token")
        
        assert result['sub'] == 'user-123'
        assert result['preferred_username'] == 'testuser'

    @patch('middleware.keycloak_auth.get_jwks_client')
    @patch('jwt.decode')
    def test_verify_token_account_audience(self, mock_decode, mock_get_client):
        mock_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test_key"
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_get_client.return_value = mock_client
        
        mock_decode.return_value = {
            'sub': 'user-123',
            'preferred_username': 'testuser',
            'aud': ['account']
        }
        
        result = verify_token("fake.jwt.token")
        assert result is not None

    @patch('middleware.keycloak_auth.get_jwks_client')
    @patch('jwt.decode')
    def test_verify_token_string_audience(self, mock_decode, mock_get_client):
        mock_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test_key"
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_get_client.return_value = mock_client
        
        mock_decode.return_value = {
            'sub': 'user-123',
            'preferred_username': 'testuser',
            'aud': 'codesnap-client'
        }
        
        result = verify_token("fake.jwt.token")
        assert result is not None

    @patch('middleware.keycloak_auth.get_jwks_client')
    @patch('jwt.decode')
    def test_verify_token_invalid_audience(self, mock_decode, mock_get_client):
        mock_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test_key"
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_get_client.return_value = mock_client
        
        mock_decode.return_value = {
            'sub': 'user-123',
            'preferred_username': 'testuser',
            'aud': ['wrong-client']
        }
        
        with pytest.raises(ValueError, match="Invalid audience"):
            verify_token("fake.jwt.token")

    @patch('middleware.keycloak_auth.get_jwks_client')
    def test_verify_token_expired(self, mock_get_client):
        mock_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test_key"
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_get_client.return_value = mock_client
        
        with patch('jwt.decode', side_effect=jwt.ExpiredSignatureError):
            with pytest.raises(ValueError, match="Token has expired"):
                verify_token("expired.jwt.token")

    @patch('middleware.keycloak_auth.get_jwks_client')
    def test_verify_token_invalid(self, mock_get_client):
        mock_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test_key"
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_get_client.return_value = mock_client
        
        with patch('jwt.decode', side_effect=jwt.InvalidTokenError("Invalid")):
            with pytest.raises(ValueError, match="Invalid token"):
                verify_token("invalid.jwt.token")

    @patch('middleware.keycloak_auth.get_jwks_client')
    def test_verify_token_general_exception(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_signing_key_from_jwt.side_effect = Exception("General error")
        
        with pytest.raises(ValueError, match="Token verification failed"):
            verify_token("error.jwt.token")

    def test_sync_user_from_token_new_user(self, test_db):
        decoded_token = {
            'sub': 'new-keycloak-id',
            'preferred_username': 'newuser'
        }
        
        user = sync_user_from_token(decoded_token)
        
        assert user is not None
        assert user.keycloak_id == 'new-keycloak-id'
        assert user.username == 'newuser'

    def test_sync_user_from_token_existing_user(self, test_db, sample_user):
        decoded_token = {
            'sub': 'test-keycloak-id',
            'preferred_username': 'updatedname'
        }
        
        user = sync_user_from_token(decoded_token)
        
        assert user.id == sample_user.id
        assert user.username == 'updatedname'

    def test_sync_user_from_token_missing_sub(self, test_db):
        decoded_token = {
            'preferred_username': 'user'
        }
        
        with pytest.raises(ValueError, match="Token missing 'sub' claim"):
            sync_user_from_token(decoded_token)

    def test_get_user_info_from_token(self, test_db, sample_user):
        decoded_token = {
            'sub': 'test-keycloak-id',
            'email': 'test@example.com',
            'preferred_username': 'testuser',
            'name': 'Test User',
            'realm_access': {'roles': ['user', 'admin']}
        }
        
        user_info = get_user_info_from_token(decoded_token, sample_user)
        
        assert user_info['id'] == sample_user.id
        assert user_info['keycloak_id'] == 'test-keycloak-id'
        assert user_info['email'] == 'test@example.com'
        assert user_info['username'] == 'testuser'
        assert user_info['name'] == 'Test User'
        assert 'user' in user_info['roles']
        assert 'admin' in user_info['roles']

    @patch('middleware.keycloak_auth.verify_token')
    @patch('middleware.keycloak_auth.sync_user_from_token')
    def test_require_auth_success(self, mock_sync, mock_verify, flask_app, sample_user):
        mock_verify.return_value = {
            'sub': 'test-keycloak-id',
            'preferred_username': 'testuser',
            'email': 'test@example.com',
            'aud': ['codesnap-client'],
            'realm_access': {'roles': ['user']}
        }
        mock_sync.return_value = sample_user
        
        with flask_app.test_client() as client:
            response = client.get(
                '/protected',
                headers={'Authorization': 'Bearer fake.jwt.token'}
            )
            
            assert response.status_code == 200
            assert response.json['user'] == 'testuser'

    def test_require_auth_no_header(self, flask_app):
        with flask_app.test_client() as client:
            response = client.get('/protected')
            
            assert response.status_code == 401
            assert 'No authorization header' in response.json['error']

    @patch('middleware.keycloak_auth.verify_token')
    def test_require_auth_invalid_token(self, mock_verify, flask_app):
        mock_verify.side_effect = ValueError("Invalid token")
        
        with flask_app.test_client() as client:
            response = client.get(
                '/protected',
                headers={'Authorization': 'Bearer invalid.token'}
            )
            
            assert response.status_code == 401
            assert 'Invalid token' in response.json['error']

    @patch('middleware.keycloak_auth.verify_token')
    def test_require_auth_exception(self, mock_verify, flask_app):
        mock_verify.side_effect = Exception("Unexpected error")
        
        with flask_app.test_client() as client:
            response = client.get(
                '/protected',
                headers={'Authorization': 'Bearer error.token'}
            )
            
            assert response.status_code == 401
            assert 'Authentication failed' in response.json['error']

    @patch('middleware.keycloak_auth.verify_token')
    @patch('middleware.keycloak_auth.sync_user_from_token')
    def test_optional_auth_with_token(self, mock_sync, mock_verify, flask_app, sample_user):
        mock_verify.return_value = {
            'sub': 'test-keycloak-id',
            'preferred_username': 'testuser',
            'email': 'test@example.com',
            'aud': ['codesnap-client'],
            'realm_access': {'roles': ['user']}
        }
        mock_sync.return_value = sample_user
        
        with flask_app.test_client() as client:
            response = client.get(
                '/optional',
                headers={'Authorization': 'Bearer fake.jwt.token'}
            )
            
            assert response.status_code == 200
            assert response.json['user'] == 'testuser'

    def test_optional_auth_without_token(self, flask_app):
        with flask_app.test_client() as client:
            response = client.get('/optional')
            
            assert response.status_code == 200
            assert response.json['user'] == 'anonymous'

    @patch('middleware.keycloak_auth.verify_token')
    def test_optional_auth_with_invalid_token(self, mock_verify, flask_app):
        mock_verify.side_effect = Exception("Invalid")
        
        with flask_app.test_client() as client:
            response = client.get(
                '/optional',
                headers={'Authorization': 'Bearer invalid.token'}
            )
            
            assert response.status_code == 200
            assert response.json['user'] == 'anonymous'

    def test_require_auth_bearer_token_format(self, flask_app):
        with patch('middleware.keycloak_auth.verify_token') as mock_verify:
            with patch('middleware.keycloak_auth.sync_user_from_token') as mock_sync:
                mock_verify.return_value = {
                    'sub': 'test-id',
                    'preferred_username': 'test',
                    'aud': ['codesnap-client'],
                    'realm_access': {'roles': []}
                }
                mock_sync.return_value = User(keycloak_id='test-id', username='test')
                
                with flask_app.test_client() as client:
                    response = client.get(
                        '/protected',
                        headers={'Authorization': 'Bearer test.jwt.token'}
                    )
                    
                    assert response.status_code == 200

    def test_require_auth_plain_token_format(self, flask_app):
        with patch('middleware.keycloak_auth.verify_token') as mock_verify:
            with patch('middleware.keycloak_auth.sync_user_from_token') as mock_sync:
                mock_verify.return_value = {
                    'sub': 'test-id',
                    'preferred_username': 'test',
                    'aud': ['codesnap-client'],
                    'realm_access': {'roles': []}
                }
                mock_sync.return_value = User(keycloak_id='test-id', username='test')
                
                with flask_app.test_client() as client:
                    response = client.get(
                        '/protected',
                        headers={'Authorization': 'plaintoken'}
                    )
                    
                    assert response.status_code == 200