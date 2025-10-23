"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/code_editor_db'
)

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production to reduce logging
    pool_pre_ping=True,
)

# For SQLite (development/testing only)
# Uncomment if you want to use SQLite for quick testing:
# engine = create_engine(
#     'sqlite:///./code_editor.db',
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
#     echo=True
# )

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def init_db():
    from models.user import User
    from models.exercise import Exercise
    from models.attempt import UserExerciseAttempt
    
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency function to get database session.
    Use this in routes to get a database session.
    
    Usage:
        db = next(get_db())
        try:
            # Use db here
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """
    Simple function to get a database session.
    Remember to close it when done!
    
    Usage:
        db = get_db_session()
        try:
            # Use db here
            db.commit()
        finally:
            db.close()
    """
    return SessionLocal()