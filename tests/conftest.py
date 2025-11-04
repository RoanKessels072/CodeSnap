import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.db import Base
from src.models.user import User
from src.models.exercise import Exercise
from src.models.attempt import Attempt
import json

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
def test_db(test_engine):
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def sample_user(test_db):
    user = User(
        keycloak_id="test-keycloak-id",
        username="testuser",
        email="test@example.com"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def sample_exercise(test_db):
    exercise = Exercise(
        name="Test Exercise",
        description="Test Description",
        difficulty=1,
        starter_code="def test(): pass",
        language="python",
        function_name="test",
        test_cases=json.dumps([{"args": [], "expected": "test"}]),
        reference_solution="def test(): return 'test'"
    )
    test_db.add(exercise)
    test_db.commit()
    test_db.refresh(exercise)
    return exercise

@pytest.fixture
def sample_attempt(test_db, sample_user, sample_exercise):
    attempt = Attempt(
        user_id=sample_user.id,
        exercise_id=sample_exercise.id,
        code_submitted="def test(): return 'test'",
        score=10,
        stars=3
    )
    test_db.add(attempt)
    test_db.commit()
    test_db.refresh(attempt)
    return attempt

@pytest.fixture
def mock_jwt_token():
    return {
        'sub': 'test-keycloak-id',
        'preferred_username': 'testuser',
        'email': 'test@example.com',
        'name': 'Test User',
        'aud': ['codesnap-client'],
        'realm_access': {'roles': ['user']}
    }

@pytest.fixture
def app():
    from src.app import app as flask_app
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()