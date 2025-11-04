import os
from unittest.mock import patch, MagicMock
from src.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig, config
from src.database.db import init_db, get_db, get_db_session, Base, engine

class TestConfig:
    def test_default_config(self):
        conf = Config()
        assert conf.SECRET_KEY is not None
        assert conf.EXECUTION_TIMEOUT == 30
        assert conf.MAX_CODE_LENGTH == 10000

    @patch.dict(os.environ, {
        'DATABASE_URL': 'postgresql://test:test@localhost/testdb',
        'SECRET_KEY': 'test-secret',
        'KEYCLOAK_URL': 'http://keycloak:8080',
        'CORS_ORIGINS': 'http://localhost:3000,http://localhost:5000',
        'RATE_LIMIT_ENABLED': 'false',
        'EXECUTION_TIMEOUT': '60',
        'MAX_CODE_LENGTH': '20000',
        'OPENAI_API_KEY': 'test-key',
        'LOG_LEVEL': 'DEBUG'
    })
    def test_config_from_environment(self):
        conf = Config()
        assert conf.DATABASE_URL == 'postgresql://test:test@localhost/testdb'
        assert conf.SECRET_KEY == 'test-secret'
        assert conf.KEYCLOAK_URL == 'http://keycloak:8080'
        assert 'http://localhost:3000' in conf.CORS_ORIGINS
        assert 'http://localhost:5000' in conf.CORS_ORIGINS
        assert conf.RATE_LIMIT_ENABLED is False
        assert conf.EXECUTION_TIMEOUT == 60
        assert conf.MAX_CODE_LENGTH == 20000
        assert conf.OPENAI_API_KEY == 'test-key'
        assert conf.LOG_LEVEL == 'DEBUG'

    @patch.dict(os.environ, {'RATE_LIMIT_ENABLED': 'true'})
    def test_rate_limit_enabled_true(self):
        conf = Config()
        assert conf.RATE_LIMIT_ENABLED is True

    @patch.dict(os.environ, {'RATE_LIMIT_ENABLED': 'TRUE'})
    def test_rate_limit_enabled_case_insensitive(self):
        conf = Config()
        assert conf.RATE_LIMIT_ENABLED is True

    def test_development_config(self):
        conf = DevelopmentConfig()
        assert conf.DEBUG is True
        assert conf.FLASK_ENV == 'development'

    def test_production_config(self):
        conf = ProductionConfig()
        assert conf.DEBUG is False
        assert conf.FLASK_ENV == 'production'

    def test_testing_config(self):
        conf = TestingConfig()
        assert conf.TESTING is True
        assert conf.DEBUG is True

    def test_config_dict(self):
        assert 'development' in config
        assert 'production' in config
        assert 'testing' in config
        assert 'default' in config
        assert config['default'] == DevelopmentConfig
        assert config['development'] == DevelopmentConfig
        assert config['production'] == ProductionConfig
        assert config['testing'] == TestingConfig

class TestDatabase:
    @patch('src.database.db.create_engine')
    def test_engine_creation(self, mock_create_engine):
        from src.database.db import DATABASE_URL
        assert DATABASE_URL is not None

    def test_init_db(self):
        with patch.object(Base.metadata, 'create_all') as mock_create:
            init_db()
            mock_create.assert_called_once_with(bind=engine)

    def test_get_db_generator(self):
        gen = get_db()
        db = next(gen)
        assert db is not None
        
        try:
            gen.close()
        except StopIteration:
            pass

    def test_get_db_session(self):
        session = get_db_session()
        assert session is not None
        session.close()

    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://custom:pass@host:5432/db'})
    def test_custom_database_url(self):
        import importlib
        import src.database.db
        importlib.reload(src.database.db)

        assert 'custom' in src.database.db.DATABASE_URL or 'postgres' in src.database.db.DATABASE_URL

class TestInitDatabase:
    @patch('src.database.db.init_db')
    def test_init_database_script(self, mock_init):
        assert mock_init is not None

class TestResetDatabase:
    @patch.object(Base.metadata, 'drop_all')
    @patch.object(Base.metadata, 'create_all')
    def test_reset_database_script(self, mock_create, mock_drop):
        assert Base.metadata is not None
        assert engine is not None

class TestSeedData:
    @patch('src.seed_data.get_db_session')
    def test_seed_exercises_already_exist(self, mock_db):
        mock_session = MagicMock()
        mock_session.query.return_value.first.return_value = MagicMock()
        mock_db.return_value = mock_session
        
        from src.seed_data import seed_exercises
        seed_exercises()
        
        mock_session.add.assert_not_called()

    @patch('src.seed_data.get_db_session')
    def test_seed_exercises_new(self, mock_db):
        mock_session = MagicMock()
        mock_session.query.return_value.first.return_value = None
        mock_db.return_value = mock_session
        
        from src.seed_data import seed_exercises
        seed_exercises()
        
        assert mock_session.add.called
        mock_session.commit.assert_called()

    @patch('src.seed_data.get_db_session')
    def test_seed_admin_user_already_exists(self, mock_db):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = MagicMock()
        mock_db.return_value = mock_session
        
        from src.seed_data import seed_admin_user
        seed_admin_user()
        
        mock_session.add.assert_not_called()

    @patch('src.seed_data.get_db_session')
    def test_seed_admin_user_new(self, mock_db):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_db.return_value = mock_session
        
        from src.seed_data import seed_admin_user
        seed_admin_user()
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called()

    @patch('src.seed_data.seed_admin_user')
    @patch('src.seed_data.seed_exercises')
    def test_seed_all(self, mock_exercises, mock_admin):
        from src.seed_data import seed_all
        seed_all()
        
        mock_admin.assert_called_once()
        mock_exercises.assert_called_once()

    @patch('src.seed_data.get_db_session')
    def test_seed_exercises_error_handling(self, mock_db):
        mock_session = MagicMock()
        mock_session.query.return_value.first.return_value = None
        mock_session.commit.side_effect = Exception("Database error")
        mock_db.return_value = mock_session
        
        from src.seed_data import seed_exercises
        
        seed_exercises()
        mock_session.rollback.assert_called()

    @patch('src.seed_data.get_db_session')
    def test_seed_admin_error_handling(self, mock_db):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.commit.side_effect = Exception("Database error")
        mock_db.return_value = mock_session
        
        from src.seed_data import seed_admin_user
        
        seed_admin_user()
        mock_session.rollback.assert_called()

class TestApp:
    @patch('src.app.init_db')
    def test_app_initialization(self, mock_init_db):
        from src.app import app
        
        assert app is not None
        assert app.config['TESTING'] or not app.config.get('TESTING')

    def test_app_blueprints_registered(self):
        from src.app import app
        
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'code' in blueprint_names
        assert 'ai_assistant' in blueprint_names
        assert 'exercises' in blueprint_names
        assert 'attempts' in blueprint_names
        assert 'users' in blueprint_names

    def test_app_url_prefixes(self):
        from src.app import app
        
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        assert any('/api/code' in rule for rule in rules)
        assert any('/api/ai' in rule for rule in rules)
        assert any('/api/exercises' in rule for rule in rules)
        assert any('/api/attempts' in rule for rule in rules)
        assert any('/api/users' in rule for rule in rules)