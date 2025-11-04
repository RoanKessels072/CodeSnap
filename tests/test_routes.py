import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from src.routes import code_execution, ai_assistant, exercises, attempts, users
from src.models.user import User
from src.models.exercise import Exercise
from src.models.attempt import Attempt

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    
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
        'email': 'test@example.com',
        'username': 'testuser',
        'roles': ['user']
    }

class TestCodeExecutionRoutes:
    @patch('routes.code_execution.require_auth')
    @patch('routes.code_execution.execute_code')
    def test_execute_code_success(self, mock_execute, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_execute.return_value = {
            'output': 'Hello, World!',
            'error': None
        }
        
        response = client.post(
            '/api/code/execute',
            json={'code': 'print("Hello, World!")', 'language': 'python'}
        )
        
        assert response.status_code == 200
        assert response.json['output'] == 'Hello, World!'

    @patch('routes.code_execution.require_auth')
    @patch('routes.code_execution.execute_code')
    def test_execute_code_with_error(self, mock_execute, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_execute.return_value = {
            'output': '',
            'error': 'SyntaxError'
        }
        
        response = client.post(
            '/api/code/execute',
            json={'code': 'bad code', 'language': 'python'}
        )
        
        assert response.status_code == 200
        assert response.json['error'] == 'SyntaxError'

class TestAIAssistantRoutes:
    @patch('routes.ai_assistant.require_auth')
    @patch('routes.ai_assistant.get_ai_assistant_feedback')
    def test_ai_assistant_success(self, mock_feedback, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_feedback.return_value = "# Add return statement"
        
        response = client.post(
            '/api/ai/ai-assistant',
            json={
                'code': 'def test(): pass',
                'language': 'python',
                'exercise_name': 'Test',
                'exercise_description': 'Test exercise',
                'reference_solution': 'def test(): return True'
            }
        )
        
        assert response.status_code == 200
        assert '# Add return statement' in response.json['response']

    @patch('routes.ai_assistant.require_auth')
    @patch('routes.ai_assistant.get_ai_assistant_feedback')
    def test_ai_assistant_error(self, mock_feedback, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_feedback.side_effect = Exception("API error")
        
        response = client.post(
            '/api/ai/ai-assistant',
            json={'code': 'test'}
        )
        
        assert response.status_code == 500
        assert 'error' in response.json

    @patch('routes.ai_assistant.require_auth')
    @patch('routes.ai_assistant.generate_ai_rival')
    def test_ai_rival_success(self, mock_rival, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_rival.return_value = "def test(): return 'rival solution'"
        
        response = client.post(
            '/api/ai/ai-rival',
            json={
                'language': 'python',
                'exercise_name': 'Test',
                'exercise_description': 'Test',
                'difficulty': 'easy'
            }
        )
        
        assert response.status_code == 200
        assert 'rival solution' in response.json['response']

    @patch('routes.ai_assistant.require_auth')
    @patch('routes.ai_assistant.generate_ai_rival')
    def test_ai_rival_error(self, mock_rival, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_rival.side_effect = Exception("API error")
        
        response = client.post(
            '/api/ai/ai-rival',
            json={'language': 'python'}
        )
        
        assert response.status_code == 500
        assert 'error' in response.json

class TestExercisesRoutes:
    @patch('routes.exercises.require_auth')
    @patch('routes.exercises.get_db')
    @patch('routes.exercises.get_all_exercises')
    def test_get_exercises(self, mock_get_all, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_get_all.return_value = [
            {'id': 1, 'name': 'Exercise 1'},
            {'id': 2, 'name': 'Exercise 2'}
        ]
        
        response = client.get('/api/exercises/exercises')
        
        assert response.status_code == 200
        assert len(response.json) == 2

    @patch('routes.exercises.require_auth')
    @patch('routes.exercises.get_db')
    @patch('routes.exercises.get_exercise_by_id')
    def test_get_exercise_by_id_success(self, mock_get, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_get.return_value = {'id': 1, 'name': 'Exercise 1'}
        
        response = client.get('/api/exercises/exercises/1')
        
        assert response.status_code == 200
        assert response.json['name'] == 'Exercise 1'

    @patch('routes.exercises.require_auth')
    @patch('routes.exercises.get_db')
    @patch('routes.exercises.get_exercise_by_id')
    def test_get_exercise_by_id_not_found(self, mock_get, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_get.return_value = None
        
        response = client.get('/api/exercises/exercises/999')
        
        assert response.status_code == 404

    @patch('routes.exercises.require_auth')
    @patch('routes.exercises.get_db')
    @patch('routes.exercises.create_exercise')
    def test_create_exercise_success(self, mock_create, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_create.return_value = {'id': 1, 'name': 'New Exercise'}
        
        response = client.post(
            '/api/exercises/exercises',
            json={'name': 'New Exercise'}
        )
        
        assert response.status_code == 201
        assert response.json['name'] == 'New Exercise'

    @patch('routes.exercises.require_auth')
    @patch('routes.exercises.get_db')
    @patch('routes.exercises.create_exercise')
    def test_create_exercise_error(self, mock_create, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_create.side_effect = Exception("Creation failed")
        
        response = client.post(
            '/api/exercises/exercises',
            json={'name': 'Exercise'}
        )
        
        assert response.status_code == 400

    @patch('routes.exercises.require_auth')
    @patch('routes.exercises.get_db')
    @patch('routes.exercises.update_exercise')
    def test_update_exercise_success(self, mock_update, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_update.return_value = {'id': 1, 'name': 'Updated'}
        
        response = client.put(
            '/api/exercises/exercises/1',
            json={'name': 'Updated'}
        )
        
        assert response.status_code == 200
        assert response.json['name'] == 'Updated'

    @patch('routes.exercises.require_auth')
    @patch('routes.exercises.get_db')
    @patch('routes.exercises.update_exercise')
    def test_update_exercise_not_found(self, mock_update, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_update.return_value = None
        
        response = client.put(
            '/api/exercises/exercises/999',
            json={'name': 'Updated'}
        )
        
        assert response.status_code == 404

    @patch('routes.exercises.require_auth')
    @patch('routes.exercises.get_db')
    @patch('routes.exercises.delete_exercise')
    def test_delete_exercise_success(self, mock_delete, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_delete.return_value = True
        
        response = client.delete('/api/exercises/exercises/1')
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.json['message']

    @patch('routes.exercises.require_auth')
    @patch('routes.exercises.get_db')
    @patch('routes.exercises.delete_exercise')
    def test_delete_exercise_not_found(self, mock_delete, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_delete.return_value = False
        
        response = client.delete('/api/exercises/exercises/999')
        
        assert response.status_code == 404

class TestAttemptsRoutes:
    @patch('routes.attempts.require_auth')
    @patch('routes.attempts.get_db_session')
    @patch('routes.attempts.get_or_create_user')
    @patch('routes.attempts.create_attempt')
    def test_submit_attempt_success(self, mock_create, mock_get_user, mock_db, mock_auth, client, mock_user_info):
        mock_auth.return_value = lambda f: f
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
        
        with patch('flask.request') as mock_request:
            mock_request.user_info = mock_user_info
            
            response = client.post(
                '/api/attempts/',
                json={'exerciseId': 1, 'code': 'test code'}
            )
            
            assert response.status_code == 200
            assert response.json['stars'] == 3

    @patch('routes.attempts.require_auth')
    def test_submit_attempt_missing_data(self, mock_auth, client, mock_user_info):
        mock_auth.return_value = lambda f: f
        
        with patch('flask.request') as mock_request:
            mock_request.user_info = mock_user_info
            
            response = client.post(
                '/api/attempts/',
                json={'code': 'test'}
            )
            
            assert response.status_code == 400
            assert 'Missing' in response.json['error']

    @patch('routes.attempts.require_auth')
    @patch('routes.attempts.get_db_session')
    @patch('routes.attempts.get_or_create_user')
    @patch('routes.attempts.create_attempt')
    def test_submit_attempt_value_error(self, mock_create, mock_get_user, mock_db, mock_auth, client, mock_user_info):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_get_user.return_value = MagicMock(id=1)
        mock_create.side_effect = ValueError("Exercise not found")
        
        with patch('flask.request') as mock_request:
            mock_request.user_info = mock_user_info
            
            response = client.post(
                '/api/attempts/',
                json={'exerciseId': 999, 'code': 'test'}
            )
            
            assert response.status_code == 404

    @patch('routes.attempts.require_auth')
    @patch('routes.attempts.get_db_session')
    @patch('routes.attempts.get_user_by_keycloak_id')
    def test_get_user_attempts_success(self, mock_get_user, mock_db, mock_auth, client, mock_user_info):
        mock_auth.return_value = lambda f: f
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        mock_db_session = MagicMock()
        mock_attempt = MagicMock()
        mock_attempt.id = 1
        mock_attempt.exercise_id = 1
        mock_attempt.score = 10
        mock_attempt.stars = 3
        mock_attempt.attempted_at = MagicMock()
        mock_attempt.attempted_at.isoformat.return_value = '2024-01-01T00:00:00'
        
        mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_attempt]
        mock_db.return_value = mock_db_session
        
        with patch('flask.request') as mock_request:
            mock_request.user_info = mock_user_info
            
            response = client.get('/api/attempts/user')
            
            assert response.status_code == 200
            assert len(response.json) == 1
            assert response.json[0]['stars'] == 3

    @patch('routes.attempts.require_auth')
    @patch('routes.attempts.get_db_session')
    @patch('routes.attempts.get_user_by_keycloak_id')
    def test_get_user_attempts_user_not_found(self, mock_get_user, mock_db, mock_auth, client, mock_user_info):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_get_user.return_value = None
        
        with patch('flask.request') as mock_request:
            mock_request.user_info = mock_user_info
            
            response = client.get('/api/attempts/user')
            
            assert response.status_code == 404

class TestUsersRoutes:
    @patch('routes.users.require_auth')
    @patch('routes.users.get_db_session')
    @patch('routes.users.get_all_users')
    def test_list_users(self, mock_get_all, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_get_all.return_value = [
            {'id': 1, 'username': 'user1'},
            {'id': 2, 'username': 'user2'}
        ]
        
        response = client.get('/api/users/')
        
        assert response.status_code == 200
        assert len(response.json) == 2

    @patch('routes.users.require_auth')
    @patch('routes.users.get_db_session')
    @patch('routes.users.sync_user_from_keycloak')
    def test_get_current_user(self, mock_sync, mock_db, mock_auth, client, mock_user_info):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.keycloak_id = 'test-keycloak-id'
        mock_user.username = 'testuser'
        mock_user.email = 'test@example.com'
        mock_user.preferred_language = 'python'
        mock_user.created_at = MagicMock()
        mock_user.created_at.isoformat.return_value = '2024-01-01T00:00:00'
        mock_user.last_login = MagicMock()
        mock_user.last_login.isoformat.return_value = '2024-01-01T00:00:00'
        mock_sync.return_value = mock_user
        
        with patch('flask.request') as mock_request:
            mock_request.user_info = mock_user_info
            
            response = client.get('/api/users/me')
            
            assert response.status_code == 200
            assert response.json['username'] == 'testuser'

    @patch('routes.users.require_auth')
    @patch('routes.users.get_db_session')
    @patch('routes.users.update_user_preference')
    def test_update_current_user(self, mock_update, mock_db, mock_auth, client, mock_user_info):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.keycloak_id = 'test-keycloak-id'
        mock_user.username = 'testuser'
        mock_user.email = 'test@example.com'
        mock_user.preferred_language = 'javascript'
        mock_user.created_at = None
        mock_user.last_login = None
        mock_update.return_value = mock_user
        
        with patch('flask.request') as mock_request:
            mock_request.user_info = mock_user_info
            
            response = client.put(
                '/api/users/me',
                json={'preferred_language': 'javascript'}
            )
            
            assert response.status_code == 200
            assert response.json['preferred_language'] == 'javascript'

    @patch('routes.users.require_auth')
    @patch('routes.users.get_db_session')
    @patch('routes.users.update_user_preference')
    def test_update_current_user_not_found(self, mock_update, mock_db, mock_auth, client, mock_user_info):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_update.return_value = None
        
        with patch('flask.request') as mock_request:
            mock_request.user_info = mock_user_info
            
            response = client.put(
                '/api/users/me',
                json={'preferred_language': 'python'}
            )
            
            assert response.status_code == 404

    @patch('routes.users.require_auth')
    @patch('routes.users.get_db_session')
    @patch('routes.users.get_user_by_id')
    def test_get_user_by_id(self, mock_get, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_get.return_value = {'id': 1, 'username': 'user1'}
        
        response = client.get('/api/users/1')
        
        assert response.status_code == 200
        assert response.json['username'] == 'user1'

    @patch('routes.users.require_auth')
    @patch('routes.users.get_db_session')
    @patch('routes.users.get_user_by_id')
    def test_get_user_by_id_not_found(self, mock_get, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_get.return_value = None
        
        response = client.get('/api/users/999')
        
        assert response.status_code == 404

    @patch('routes.users.require_auth')
    @patch('routes.users.get_db_session')
    @patch('routes.users.delete_user')
    def test_delete_user_success(self, mock_delete, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_delete.return_value = True
        
        response = client.delete('/api/users/test-keycloak-id')
        
        assert response.status_code == 200
        assert 'deleted successfully' in response.json['message']

    @patch('routes.users.require_auth')
    @patch('routes.users.get_db_session')
    @patch('routes.users.delete_user')
    def test_delete_user_not_found(self, mock_delete, mock_db, mock_auth, client):
        mock_auth.return_value = lambda f: f
        mock_db.return_value = MagicMock()
        mock_delete.return_value = False
        
        response = client.delete('/api/users/non-existent')
        
        assert response.status_code == 404