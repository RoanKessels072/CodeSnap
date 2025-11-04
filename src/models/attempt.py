from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db import Base

class Attempt(Base):
    __tablename__ = 'user_exercise_attempts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercises.id'), nullable=False)
    
    code_submitted = Column(Text, nullable=False)
    score = Column(Integer, nullable=False, default=0)
    stars = Column(Integer, nullable=False, default=0)
    attempted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship('User', back_populates='attempts')
    exercise = relationship('Exercise', back_populates='attempts')