from src.services.user_service import (
    get_user_by_keycloak_id,
    get_user_by_id,
    sync_user_from_keycloak,
    get_or_create_user,
    get_all_users,
    update_user_preference,
    delete_user,
    user_to_dict
)
from src.models.user import User

class TestUserService:
    def test_get_user_by_keycloak_id(self, test_db, sample_user):
        user = get_user_by_keycloak_id(test_db, "test-keycloak-id")
        assert user is not None
        assert user.keycloak_id == "test-keycloak-id"

    def test_get_user_by_keycloak_id_not_found(self, test_db):
        user = get_user_by_keycloak_id(test_db, "non-existent")
        assert user is None

    def test_get_user_by_id(self, test_db, sample_user):
        user = get_user_by_id(test_db, sample_user.id)
        assert user is not None
        assert user.id == sample_user.id

    def test_get_user_by_id_not_found(self, test_db):
        user = get_user_by_id(test_db, 99999)
        assert user is None

    def test_sync_user_from_keycloak_create_new(self, test_db):
        user = sync_user_from_keycloak(
            test_db,
            keycloak_id="new-user-id",
            username="newuser",
        )
        assert user is not None
        assert user.keycloak_id == "new-user-id"
        assert user.username == "newuser"

    def test_sync_user_from_keycloak_update_existing(self, test_db, sample_user):
        original_login = sample_user.last_login
        
        user = sync_user_from_keycloak(
            test_db,
            keycloak_id="test-keycloak-id",
            username="updateduser",
        )
        
        assert user.username == "updateduser"
        assert user.last_login >= original_login

    def test_sync_user_partial_update(self, test_db, sample_user):
        user = sync_user_from_keycloak(
            test_db,
            keycloak_id="test-keycloak-id",
            username="newusername"
        )
        
        assert user.username == "newusername"

    def test_get_or_create_user_existing(self, test_db, sample_user):
        user = get_or_create_user(
            test_db,
            keycloak_id="test-keycloak-id",
            username="testuser",
        )
        assert user.id == sample_user.id

    def test_get_or_create_user_new(self, test_db):
        user = get_or_create_user(
            test_db,
            keycloak_id="brand-new-id",
            username="brandnew",
        )
        assert user is not None
        assert user.keycloak_id == "brand-new-id"

    def test_get_all_users(self, test_db, sample_user):
        user2 = User(keycloak_id="user2", username="user2")
        test_db.add(user2)
        test_db.commit()
        
        users = get_all_users(test_db)
        assert len(users) == 2
        assert all(isinstance(u, dict) for u in users)

    def test_update_user_preference(self, test_db, sample_user):
        data = {"preferred_language": "python"}
        user = update_user_preference(test_db, "test-keycloak-id", data)
        
        assert user is not None
        assert user.preferred_language == "python"

    def test_update_user_preference_not_found(self, test_db):
        data = {"preferred_language": "python"}
        user = update_user_preference(test_db, "non-existent", data)
        assert user is None

    def test_delete_user(self, test_db, sample_user):
        result = delete_user(test_db, "test-keycloak-id")
        assert result is True
        
        user = get_user_by_keycloak_id(test_db, "test-keycloak-id")
        assert user is None

    def test_delete_user_not_found(self, test_db):
        result = delete_user(test_db, "non-existent")
        assert result is False

    def test_user_to_dict(self, test_db, sample_user):
        user_dict = user_to_dict(sample_user)
        
        assert user_dict["id"] == sample_user.id
        assert user_dict["keycloak_id"] == sample_user.keycloak_id
        assert user_dict["username"] == sample_user.username
        assert "created_at" in user_dict
        assert "last_login" in user_dict

    def test_user_to_dict_none_dates(self, test_db):
        user = User(keycloak_id="test")
        user.created_at = None
        user.last_login = None
        
        user_dict = user_to_dict(user)
        assert user_dict["created_at"] is None
        assert user_dict["last_login"] is None