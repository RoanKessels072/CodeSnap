from flask import Blueprint, jsonify, request
from database.db import get_db_session
from models.exercise import Exercise

bp = Blueprint('exercises', __name__)

@bp.route('/', methods=['GET'])
def get_exercises():
    """Get all exercises"""
    db = get_db_session()
    try:
        exercises = db.query(Exercise).all()
        
        # Convert to dict manually to avoid SQLAlchemy issues
        result = []
        for ex in exercises:
            result.append({
                'id': ex.id,
                'name': ex.name,
                'description': ex.description,
                'difficulty': ex.difficulty,
                'starter_code': ex.starter_code,
                'language': ex.language,
                'test_cases': ex.test_cases,
                'reference_solution': ex.reference_solution,
                'created_at': ex.created_at.isoformat() if ex.created_at else None
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    """Get a specific exercise by ID"""
    db = get_db_session()
    try:
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        
        if not exercise:
            return jsonify({'error': 'Exercise not found'}), 404
        
        return jsonify({
            'id': exercise.id,
            'name': exercise.name,
            'description': exercise.description,
            'difficulty': exercise.difficulty,
            'starter_code': exercise.starter_code,
            'language': exercise.language,
            'test_cases': exercise.test_cases,
            'reference_solution': exercise.reference_solution,
            'created_at': exercise.created_at.isoformat() if exercise.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/', methods=['POST'])
def create_exercise():
    """Create a new exercise"""
    db = get_db_session()
    try:
        data = request.get_json()
        
        exercise = Exercise(
            name=data.get('name'),
            description=data.get('description'),
            difficulty=data.get('difficulty'),
            starter_code=data.get('starter_code'),
            language=data.get('language'),
            test_cases=data.get('test_cases', []),
            reference_solution=data.get('reference_solution')
        )
        
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        
        return jsonify({
            'id': exercise.id,
            'name': exercise.name,
            'description': exercise.description,
            'difficulty': exercise.difficulty,
            'starter_code': exercise.starter_code,
            'language': exercise.language,
            'test_cases': exercise.test_cases,
            'reference_solution': exercise.reference_solution,
            'created_at': exercise.created_at.isoformat() if exercise.created_at else None
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:exercise_id>', methods=['PUT'])
def update_exercise(exercise_id):
    """Update an existing exercise"""
    db = get_db_session()
    try:
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        
        if not exercise:
            return jsonify({'error': 'Exercise not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            exercise.name = data['name']
        if 'description' in data:
            exercise.description = data['description']
        if 'difficulty' in data:
            exercise.difficulty = data['difficulty']
        if 'starter_code' in data:
            exercise.starter_code = data['starter_code']
        if 'language' in data:
            exercise.language = data['language']
        if 'test_cases' in data:
            exercise.test_cases = data['test_cases']
        if 'reference_solution' in data:
            exercise.reference_solution = data['reference_solution']
        
        db.commit()
        db.refresh(exercise)
        
        return jsonify({
            'id': exercise.id,
            'name': exercise.name,
            'description': exercise.description,
            'difficulty': exercise.difficulty,
            'starter_code': exercise.starter_code,
            'language': exercise.language,
            'test_cases': exercise.test_cases,
            'reference_solution': exercise.reference_solution,
            'created_at': exercise.created_at.isoformat() if exercise.created_at else None
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    """Delete an exercise"""
    db = get_db_session()
    try:
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        
        if not exercise:
            return jsonify({'error': 'Exercise not found'}), 404
        
        db.delete(exercise)
        db.commit()
        
        return jsonify({'message': 'Exercise deleted successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()