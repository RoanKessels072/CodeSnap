from src.models.user import User
from src.models.exercise import Exercise
from src.models.attempt import Attempt
import json

class TestUserModel:
    def test_create_user(self, test_db):
        user = User(
            keycloak_id="test-id",
            username="testuser",
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.id is not None
        assert user.keycloak_id == "test-id"
        assert user.username == "testuser"
        assert user.created_at is not None
        assert user.last_login is not None

    def test_user_relationships(self, test_db, sample_user, sample_exercise):
        attempt = Attempt(
            user_id=sample_user.id,
            exercise_id=sample_exercise.id,
            code_submitted="test code",
            score=10,
            stars=3
        )
        test_db.add(attempt)
        test_db.commit()
        
        assert len(sample_user.attempts) == 1
        assert sample_user.attempts[0].code_submitted == "test code"

class TestExerciseModel:
    def test_create_exercise(self, test_db):
        test_cases = [{"args": [1, 2], "expected": 3}]
        exercise = Exercise(
            name="Add Numbers",
            description="Add two numbers",
            difficulty=1,
            starter_code="def add(a, b): pass",
            language="python",
            function_name="add",
            test_cases=json.dumps(test_cases),
            reference_solution="def add(a, b): return a + b"
        )
        test_db.add(exercise)
        test_db.commit()
        test_db.refresh(exercise)
        
        assert exercise.id is not None
        assert exercise.name == "Add Numbers"
        assert exercise.difficulty == 1
        assert exercise.language == "python"
        assert exercise.created_at is not None
        assert json.loads(exercise.test_cases) == test_cases

    def test_exercise_relationships(self, test_db, sample_exercise, sample_user):
        attempt = Attempt(
            user_id=sample_user.id,
            exercise_id=sample_exercise.id,
            code_submitted="test code",
            score=10,
            stars=3
        )
        test_db.add(attempt)
        test_db.commit()
        
        assert len(sample_exercise.attempts) == 1
        assert sample_exercise.attempts[0].exercise_id == sample_exercise.id

class TestAttemptModel:
    def test_create_attempt(self, test_db, sample_user, sample_exercise):
        attempt = Attempt(
            user_id=sample_user.id,
            exercise_id=sample_exercise.id,
            code_submitted="def test(): return 'hello'",
            score=8,
            stars=2
        )
        test_db.add(attempt)
        test_db.commit()
        test_db.refresh(attempt)
        
        assert attempt.id is not None
        assert attempt.user_id == sample_user.id
        assert attempt.exercise_id == sample_exercise.id
        assert attempt.score == 8
        assert attempt.stars == 2
        assert attempt.attempted_at is not None

    def test_attempt_relationships(self, test_db, sample_attempt, sample_user, sample_exercise):
        assert sample_attempt.user.id == sample_user.id
        assert sample_attempt.exercise.id == sample_exercise.id