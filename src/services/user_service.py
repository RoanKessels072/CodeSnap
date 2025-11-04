from sqlalchemy.orm import Session
from datetime import datetime, timezone
from src.models.user import User


def get_user_by_keycloak_id(db: Session, keycloak_id: str):
    return db.query(User).filter(User.keycloak_id == keycloak_id).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


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


def get_or_create_user(db: Session, keycloak_id: str, username: str):
    user = get_user_by_keycloak_id(db, keycloak_id)
    if user:
        return sync_user_from_keycloak(db, keycloak_id, username)
    else:
        return sync_user_from_keycloak(db, keycloak_id, username)


def get_all_users(db: Session):
    users = db.query(User).all()
    return [user_to_dict(u) for u in users]


def update_user_preference(db: Session, keycloak_id: str, data: dict):
    user = get_user_by_keycloak_id(db, keycloak_id)
    if not user:
        return None

    if "preferred_language" in data:
        user.preferred_language = data["preferred_language"]

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, keycloak_id: str):
    user = get_user_by_keycloak_id(db, keycloak_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def user_to_dict(user: User):
    return {
        "id": user.id,
        "keycloak_id": user.keycloak_id,
        "username": user.username,
        "preferred_language": user.preferred_language,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None
    }
