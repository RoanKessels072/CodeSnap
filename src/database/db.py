from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

def get_engine():
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/code_editor_db')
    return create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

def get_db_session():
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_db():
    db = get_db_session()()
    try:
        yield db
    finally:
        db.close()

def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
