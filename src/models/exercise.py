# models/exercise.py
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db import Base

class Exercise(Base):
    __tablename__ = 'exercises'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Integer, nullable=False)  # 1-5
    starter_code = Column(Text, nullable=False)  # Initial code template
    language = Column(String(50), nullable=False)  # 'python' or 'javascript'
    
    # Test cases for validation (stored as JSON)
    # Example: [{"input": "5", "expected_output": "25"}, ...]
    test_cases = Column(JSON, nullable=False)
    
    # Optional: Reference solution for display/hints
    reference_solution = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    attempts = relationship('UserExerciseAttempt', back_populates='exercise')