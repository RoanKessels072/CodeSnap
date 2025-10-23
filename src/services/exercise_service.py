from sqlalchemy.orm import Session
from models.exercise import Exercise
from datetime import datetime, timezone

def create_exercise(db: Session, exercise_data: dict) -> Exercise:
    new_exercise = Exercise(**exercise_data)
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise

def get_exercises(db: Session) -> list[Exercise]:
    return db.query(Exercise).order_by(Exercise.created_at.desc()).all()

def get_exercise_by_id(db: Session, exercise_id: int) -> Exercise | None:
    return db.query(Exercise).filter(Exercise.id == exercise_id).first()

def update_exercise(db: Session, exercise_id: int, updates: dict) -> Exercise | None:
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        return None

    for key, value in updates.items():
        setattr(exercise, key, value)

    exercise.created_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(exercise)
    return exercise


def delete_exercise(db: Session, exercise_id: int) -> bool:
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        return False

    db.delete(exercise)
    db.commit()
    return True
