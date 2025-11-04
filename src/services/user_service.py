from sqlalchemy.orm import Session
from models.user import User
from datetime import datetime, timezone

def sync_user_from_keycloak(db: Session, keycloak_id: str, username: str = None):
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    
    if not user:
        user = User(
            keycloak_id=keycloak_id,
            username=username,
            last_login=datetime.now(timezone.utc)
        )
        db.add(user)
    else:
        user.last_login = datetime.now(timezone.utc)
        if username and user.username != username:
            user.username = username
    
    db.commit()
    db.refresh(user)
    return user

def get_user_by_keycloak_id(db: Session, keycloak_id: str):
    return db.query(User).filter(User.keycloak_id == keycloak_id).first()