from sqlalchemy import Column, String, Text, Integer, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db import Base

class Exercise(Base):
    __tablename__ = 'exercises'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Integer, nullable=False)
    starter_code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False) 
    function_name = Column(String, nullable=False)   
    test_cases = Column(JSON, nullable=False)
    reference_solution = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    attempts = relationship('Attempt', back_populates='exercise')