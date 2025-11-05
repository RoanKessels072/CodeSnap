from sqlalchemy.orm import Session
from models.exercise import Exercise
import json

def get_all_exercises(db: Session):
    exercises = db.query(Exercise).all()
    return [exercise_to_dict(e) for e in exercises]

def get_exercise_by_id(db: Session, exercise_id: int):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    return exercise_to_dict(exercise) if exercise else None

def create_exercise(db: Session, data: dict):
    try:
        new_exercise = Exercise(
            name=data["name"],
            description=data.get("description", ""),
            language=data.get("language", "python"),
            difficulty=data.get("difficulty", "easy"),
            function_name=data.get("function_name", ""),
            test_cases=json.dumps(data.get("test_cases", [])),
            reference_solution=data.get("reference_solution", ""),
            starter_code=data.get("starter_code", "")
        )
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        return exercise_to_dict(new_exercise)
    except KeyError as e:
        raise ValueError(f"Missing required field: {e}")

def update_exercise(db: Session, exercise_id: int, data: dict):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        return None

    for key, value in data.items():
        if hasattr(exercise, key):
            if key == "test_cases" and isinstance(value, list):
                setattr(exercise, key, json.dumps(value))
            else:
                setattr(exercise, key, value)
    db.commit()
    db.refresh(exercise)
    return exercise_to_dict(exercise)

def delete_exercise(db: Session, exercise_id: int):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        return False
    db.delete(exercise)
    db.commit()
    return True

def exercise_to_dict(exercise: Exercise):
    return {
        "id": exercise.id,
        "name": exercise.name,
        "description": exercise.description,
        "language": exercise.language,
        "difficulty": exercise.difficulty,
        "function_name": exercise.function_name,
        "test_cases": json.loads(exercise.test_cases) if exercise.test_cases else [],
        "reference_solution": exercise.reference_solution,
    }
