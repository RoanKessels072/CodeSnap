import pytest
import json
from src.services.exercise_service import (
    get_all_exercises,
    get_exercise_by_id,
    create_exercise,
    update_exercise,
    delete_exercise,
    exercise_to_dict
)
from src.models.exercise import Exercise

class TestExerciseService:
    def test_get_all_exercises(self, test_db, sample_exercise):
        ex2 = Exercise(
            name="Test 2",
            description="Desc 2",
            difficulty=2,
            starter_code="code",
            language="python",
            function_name="test2",
            test_cases=json.dumps([]),
            reference_solution="solution"
        )
        test_db.add(ex2)
        test_db.commit()
        
        exercises = get_all_exercises(test_db)
        assert len(exercises) == 2
        assert all(isinstance(e, dict) for e in exercises)

    def test_get_exercise_by_id(self, test_db, sample_exercise):
        exercise = get_exercise_by_id(test_db, sample_exercise.id)
        assert exercise is not None
        assert exercise["id"] == sample_exercise.id
        assert exercise["name"] == sample_exercise.name

    def test_get_exercise_by_id_not_found(self, test_db):
        exercise = get_exercise_by_id(test_db, 99999)
        assert exercise is None

    def test_create_exercise_full(self, test_db):
        data = {
            "name": "New Exercise",
            "description": "New Description",
            "language": "python",
            "difficulty": "medium",
            "function_name": "new_func",
            "test_cases": [{"args": [1], "expected": 2}],
            "reference_solution": "def new_func(x): return x + 1"
        }
        
        exercise = create_exercise(test_db, data)
        assert exercise is not None
        assert exercise["name"] == "New Exercise"
        assert exercise["language"] == "python"
        assert len(exercise["test_cases"]) == 1

    def test_create_exercise_minimal(self, test_db):
        data = {
            "name": "Minimal Exercise"
        }
        
        exercise = create_exercise(test_db, data)
        assert exercise is not None
        assert exercise["name"] == "Minimal Exercise"
        assert exercise["description"] == ""
        assert exercise["language"] == "python"
        assert exercise["difficulty"] == "easy"

    def test_create_exercise_missing_name(self, test_db):
        data = {"description": "No name"}
        
        with pytest.raises(ValueError, match="Missing required field"):
            create_exercise(test_db, data)

    def test_update_exercise(self, test_db, sample_exercise):
        data = {
            "name": "Updated Name",
            "difficulty": 3
        }
        
        updated = update_exercise(test_db, sample_exercise.id, data)
        assert updated is not None
        assert updated["name"] == "Updated Name"
        assert updated["difficulty"] == 3

    def test_update_exercise_test_cases(self, test_db, sample_exercise):
        new_test_cases = [{"args": [5], "expected": 10}]
        data = {"test_cases": new_test_cases}
        
        updated = update_exercise(test_db, sample_exercise.id, data)
        assert updated["test_cases"] == new_test_cases

    def test_update_exercise_not_found(self, test_db):
        data = {"name": "New Name"}
        updated = update_exercise(test_db, 99999, data)
        assert updated is None

    def test_update_exercise_invalid_field(self, test_db, sample_exercise):
        data = {"invalid_field": "value", "name": "Valid Update"}
        
        updated = update_exercise(test_db, sample_exercise.id, data)
        assert updated["name"] == "Valid Update"
        assert not hasattr(updated, "invalid_field")

    def test_delete_exercise(self, test_db, sample_exercise):
        result = delete_exercise(test_db, sample_exercise.id)
        assert result is True
        
        exercise = get_exercise_by_id(test_db, sample_exercise.id)
        assert exercise is None

    def test_delete_exercise_not_found(self, test_db):
        result = delete_exercise(test_db, 99999)
        assert result is False

    def test_exercise_to_dict(self, test_db, sample_exercise):
        exercise_dict = exercise_to_dict(sample_exercise)
        
        assert exercise_dict["id"] == sample_exercise.id
        assert exercise_dict["name"] == sample_exercise.name
        assert exercise_dict["description"] == sample_exercise.description
        assert exercise_dict["language"] == sample_exercise.language
        assert exercise_dict["difficulty"] == sample_exercise.difficulty
        assert exercise_dict["function_name"] == sample_exercise.function_name
        assert isinstance(exercise_dict["test_cases"], list)
        assert exercise_dict["reference_solution"] == sample_exercise.reference_solution

    def test_exercise_to_dict_null_test_cases(self, test_db):
        exercise = Exercise(
            name="Test",
            description="Test",
            difficulty=1,
            starter_code="code",
            language="python",
            function_name="test",
            test_cases=None,
            reference_solution="solution"
        )
        test_db.add(exercise)
        test_db.commit()
        test_db.refresh(exercise)
        
        exercise_dict = exercise_to_dict(exercise)
        assert exercise_dict["test_cases"] == []