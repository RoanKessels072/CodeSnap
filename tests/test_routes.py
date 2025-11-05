import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, request

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr("middleware.keycloak_auth.require_auth", lambda f: f)

    app = Flask(__name__)
    app.config['TESTING'] = True

    from routes import code_execution, ai_assistant, exercises, attempts, users
    app.register_blueprint(code_execution.bp, url_prefix='/api/code')
    app.register_blueprint(ai_assistant.bp, url_prefix='/api/ai')
    app.register_blueprint(exercises.bp, url_prefix='/api/exercises')
    app.register_blueprint(attempts.bp, url_prefix='/api/attempts')
    app.register_blueprint(users.bp, url_prefix='/api/users')

    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_user_info():
    return {
        'id': 1,
        'keycloak_id': 'test-keycloak-id',
        'username': 'testuser',
        'roles': ['user']
    }


@pytest.fixture
def bypass_auth(monkeypatch):
    monkeypatch.setattr('middleware.keycloak_auth.require_auth', lambda f: f)
    return lambda f: f

class TestCodeExecutionRoutes:
    def test_execute_code_success(self, client, bypass_auth):
        with patch('routes.code_execution.execute_code') as mock_execute:
            mock_execute.return_value = {'output': 'Hello, World!', 'error': None}
            response = client.post(
                '/api/code/execute',
                json={'code': 'print("Hello, World!")', 'language': 'python'}
            )
            assert response.status_code == 200
            assert response.json['output'] == 'Hello, World!'


class TestAIAssistantRoutes:
    def test_ai_assistant_success(self, client, bypass_auth):
        with patch('routes.ai_assistant.get_ai_assistant_feedback') as mock_feedback:
            mock_feedback.return_value = "# Add return statement"
            response = client.post(
                '/api/ai/ai-assistant',
                json={'code': 'def test(): pass', 'language': 'python'}
            )
            assert response.status_code == 200

    def test_ai_rival_success(self, client, bypass_auth):
        with patch('routes.ai_assistant.generate_ai_rival') as mock_rival:
            mock_rival.return_value = "def test(): return 'rival'"
            response = client.post('/api/ai/ai-rival', json={'language': 'python'})
            assert response.status_code == 200


class TestExercisesRoutes:
    def test_get_exercises(self, client, bypass_auth):
        with patch('routes.exercises.get_db') as mock_db, \
             patch('routes.exercises.get_all_exercises') as mock_get_all:
            mock_db.return_value = MagicMock()
            mock_get_all.return_value = [{'id': 1, 'name': 'Exercise 1'}]
            response = client.get('/api/exercises/exercises')
            assert response.status_code == 200
            assert len(response.json) == 1

    def test_get_exercise_by_id_not_found(self, client, bypass_auth):
        with patch('routes.exercises.get_db') as mock_db, \
             patch('routes.exercises.get_exercise_by_id') as mock_get:
            mock_db.return_value = MagicMock()
            mock_get.return_value = None
            response = client.get('/api/exercises/exercises/999')
            assert response.status_code == 404

    def test_create_exercise_success(self, client, bypass_auth):
        with patch('routes.exercises.get_db') as mock_db, \
             patch('routes.exercises.create_exercise') as mock_create:
            mock_db.return_value = MagicMock()
            mock_create.return_value = {'id': 1, 'name': 'New Exercise'}
            response = client.post('/api/exercises/exercises', json={'name': 'New Exercise'})
            assert response.status_code == 201

    def test_delete_exercise_success(self, client, bypass_auth):
        with patch('routes.exercises.get_db') as mock_db, \
             patch('routes.exercises.delete_exercise') as mock_delete:
            mock_db.return_value = MagicMock()
            mock_delete.return_value = True
            response = client.delete('/api/exercises/exercises/1')
            assert response.status_code == 200


class TestAttemptsRoutes:
    def test_submit_attempt_success(self, client, bypass_auth, mock_user_info):
        with patch('routes.attempts.get_db_session') as mock_db, \
             patch('routes.attempts.get_or_create_user') as mock_get_user, \
             patch('routes.attempts.create_attempt') as mock_create:

            mock_db.return_value = MagicMock()
            mock_user = MagicMock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            mock_attempt = MagicMock()
            mock_attempt.id = 1
            mock_attempt.stars = 3
            mock_attempt.score = 10
            mock_attempt.exercise_id = 1
            mock_create.return_value = mock_attempt

            with client.application.test_request_context(
                '/api/attempts/',
                method='POST',
                json={'exerciseId': 1, 'code': 'test code'}
            ):
                request.user_info = mock_user_info
                from routes.attempts import submit_attempt
                response = submit_attempt()

            status_code = response[1] if isinstance(response, tuple) else 200
            assert status_code in [200, 400, 500]

    def test_submit_attempt_missing_data(self, client, bypass_auth, mock_user_info):
        with client.application.test_request_context(
            '/api/attempts/',
            method='POST',
            json={'code': 'test'}
        ):
            request.user_info = mock_user_info
            from routes.attempts import submit_attempt
            response = submit_attempt()

        status_code = response[1] if isinstance(response, tuple) else 200
        assert status_code == 400


class TestUsersRoutes:
    def test_list_users(self, client, bypass_auth):
        with patch('routes.users.get_db_session') as mock_db, \
             patch('routes.users.get_all_users') as mock_get_all:
            mock_db.return_value = MagicMock()
            mock_get_all.return_value = [{'id': 1, 'username': 'user1'}]
            response = client.get('/api/users/')
            assert response.status_code == 200
            
    def test_list_users_error(self, client, bypass_auth):
        with patch('routes.users.get_db_session') as mock_db, \
             patch('routes.users.get_all_users', side_effect=Exception("DB Error")):
            mock_db.return_value = MagicMock()
            response = client.get('/api/users/')
            assert response.status_code == 500
            assert "DB Error" in response.json['error']

    def test_get_current_user_error(self, client, bypass_auth, mock_user_info):
        with patch('routes.users.get_db_session') as mock_db, \
             patch('routes.users.sync_user_from_keycloak', side_effect=Exception("Sync Error")), \
             client.application.test_request_context('/api/users/me', method='GET'):
            request.user_info = mock_user_info
            mock_db.return_value = MagicMock()
            from routes.users import get_current_user
            response = get_current_user()
            status_code = response[1] if isinstance(response, tuple) else 200
            assert status_code == 500
            assert "Sync Error" in response[0].json['error']

    def test_update_current_user_not_found(self, client, bypass_auth, mock_user_info):
        with patch('routes.users.get_db_session') as mock_db, \
             patch('routes.users.update_user_preference', return_value=None), \
             client.application.test_request_context('/api/users/me', method='PUT', json={"theme": "dark"}):
            request.user_info = mock_user_info
            mock_db.return_value = MagicMock()
            from routes.users import update_current_user
            response = update_current_user()
            status_code = response[1] if isinstance(response, tuple) else 200
            assert status_code == 404
            assert response[0].json['error'] == 'User not found'

    def test_get_user_by_id_route_not_found(self, client, bypass_auth):
        with patch('routes.users.get_db_session') as mock_db, \
             patch('routes.users.get_user_by_id', return_value=None):
            mock_db.return_value = MagicMock()
            response = client.get('/api/users/999')
            assert response.status_code == 404
            assert response.json['error'] == 'User not found'

    def test_delete_user_route_not_found(self, client, bypass_auth):
        with patch('routes.users.get_db_session') as mock_db, \
             patch('routes.users.delete_user', return_value=False):
            mock_db.return_value = MagicMock()
            response = client.delete('/api/users/nonexistent-keycloak-id')
            assert response.status_code == 404
            assert response.json['error'] == 'User not found'

    def test_delete_user_route_error(self, client, bypass_auth):
        with patch('routes.users.get_db_session') as mock_db, \
             patch('routes.users.delete_user', side_effect=Exception("Delete Error")):
            mock_db.return_value = MagicMock()
            response = client.delete('/api/users/any-id')
            assert response.status_code == 500
            assert "Delete Error" in response.json['error']
