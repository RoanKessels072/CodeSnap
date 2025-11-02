from sqlalchemy.orm import Session
from models.user import User
from datetime import datetime, timezone

def get_or_create_user(db: Session, keycloak_id: str, email: str, username: str) -> User:
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    
    if user:
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        return user
    
    user = User(
        keycloak_id=keycloak_id,
        email=email,
        username=username
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

def get_user_by_keycloak_id(db: Session, keycloak_id: str) -> User | None:
    return db.query(User).filter(User.keycloak_id == keycloak_id).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()