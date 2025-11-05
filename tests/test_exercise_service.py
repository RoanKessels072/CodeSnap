import sys
from pathlib import Path
import json
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.exercise_service import (
    get_all_exercises,
    get_exercise_by_id,
    create_exercise,
    update_exercise,
    delete_exercise,
    exercise_to_dict
)
from models.exercise import Exercise

class TestExerciseService:

    def test_get_all_exercises_empty(self, test_db):
        exercises = get_all_exercises(test_db)
        assert exercises == []

    def test_get_all_exercises_multiple(self, test_db, sample_exercise):
        ex2 = Exercise(
            name="Second Exercise",
            description="Desc 2",
            difficulty="medium",
            language="python",
            function_name="second_func",
            test_cases=json.dumps([]),
            reference_solution="solution",
            starter_code="def func(): pass"
        )
        test_db.add(ex2)
        test_db.commit()
        
        exercises = get_all_exercises(test_db)
        assert len(exercises) == 2
        assert all(isinstance(e, dict) for e in exercises)

    def test_get_exercise_by_id_found(self, test_db, sample_exercise):
        exercise = get_exercise_by_id(test_db, sample_exercise.id)
        assert exercise is not None
        assert exercise["id"] == sample_exercise.id

    def test_get_exercise_by_id_not_found(self, test_db):
        exercise = get_exercise_by_id(test_db, 99999)
        assert exercise is None

    def test_create_exercise_complete(self, test_db):
        data = {
            "name": "Complete Exercise",
            "description": "Full Desc",
            "language": "python",
            "difficulty": "hard",
            "function_name": "full_func",
            "test_cases": [{"args": [1], "expected": 2}],
            "reference_solution": "def full_func(x): return x",
            "starter_code": "def func(): pass"
        }
        exercise = create_exercise(test_db, data)
        assert exercise["name"] == "Complete Exercise"
        assert exercise["test_cases"][0]["expected"] == 2

    def test_create_exercise_minimal(self, test_db):
        data = {
            "name": "Minimal Exercise",
            "starter_code": "def func(): pass"
        }
        exercise = create_exercise(test_db, data)
        assert exercise["name"] == "Minimal Exercise"
        assert exercise["description"] == ""
        assert exercise["difficulty"] == "easy"
        assert exercise["test_cases"] == []

    def test_create_exercise_missing_required_field(self, test_db):
        data = {"description": "Missing name"}
        with pytest.raises(ValueError, match="Missing required field"):
            create_exercise(test_db, data)

    def test_update_exercise_existing(self, test_db, sample_exercise):
        data = {"name": "Updated Name", "difficulty": "medium"}
        updated = update_exercise(test_db, sample_exercise.id, data)
        assert updated["name"] == "Updated Name"
        assert updated["difficulty"] == "medium"

    def test_update_exercise_test_cases_list(self, test_db, sample_exercise):
        new_cases = [{"args": [5], "expected": 10}]
        updated = update_exercise(test_db, sample_exercise.id, {"test_cases": new_cases})
        assert updated["test_cases"] == new_cases

    def test_update_exercise_not_found(self, test_db):
        updated = update_exercise(test_db, 99999, {"name": "Nope"})
        assert updated is None

    def test_update_exercise_invalid_field_ignored(self, test_db, sample_exercise):
        data = {"invalid_field": "value", "name": "Valid Update"}
        updated = update_exercise(test_db, sample_exercise.id, data)
        assert updated["name"] == "Valid Update"
        raw = test_db.query(Exercise).filter_by(id=sample_exercise.id).first()
        assert not hasattr(raw, "invalid_field")

    def test_delete_exercise_existing(self, test_db, sample_exercise):
        result = delete_exercise(test_db, sample_exercise.id)
        assert result is True
        assert get_exercise_by_id(test_db, sample_exercise.id) is None

    def test_delete_exercise_nonexistent(self, test_db):
        result = delete_exercise(test_db, 99999)
        assert result is False

    def test_exercise_to_dict_with_data(self, test_db, sample_exercise):
        d = exercise_to_dict(sample_exercise)
        assert d["id"] == sample_exercise.id
        assert isinstance(d["test_cases"], list)

    def test_exercise_to_dict_null_test_cases(self, test_db):
        exercise = Exercise(
            name="No Cases",
            description="None",
            difficulty="easy",
            language="python",
            function_name="none_func",
            test_cases=None,
            reference_solution="",
            starter_code="def func(): pass"
        )
        test_db.add(exercise)
        test_db.commit()
        test_db.refresh(exercise)
        d = exercise_to_dict(exercise)
        assert d["test_cases"] == []

    def test_exercise_to_dict_empty_string_test_cases(self, test_db):
        exercise = Exercise(
            name="Empty Cases",
            description="Desc",
            difficulty="easy",
            language="python",
            function_name="empty_func",
            test_cases="",
            reference_solution="",
            starter_code="def func(): pass"
        )
        test_db.add(exercise)
        test_db.commit()
        test_db.refresh(exercise)
        d = exercise_to_dict(exercise)
        assert d["test_cases"] == []
