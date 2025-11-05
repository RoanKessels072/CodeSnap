import sys
from pathlib import Path
import importlib

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os
from unittest.mock import patch, MagicMock

class TestConfig:
    def test_default_config(self):
        from config import Config
        conf = Config()
        assert conf.SECRET_KEY is not None
        assert conf.EXECUTION_TIMEOUT == 30
        assert conf.MAX_CODE_LENGTH == 10000

    @patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret',
        'RATE_LIMIT_ENABLED': 'false',
        'EXECUTION_TIMEOUT': '60'
    }, clear=False)
    
    def test_config_from_environment(self):
        import config
        importlib.reload(config)
        conf = config.Config()
        assert conf.SECRET_KEY == 'test-secret'
        assert conf.RATE_LIMIT_ENABLED is False
        assert conf.EXECUTION_TIMEOUT == 60

    def test_development_config(self):
        from config import DevelopmentConfig
        conf = DevelopmentConfig()
        assert conf.DEBUG is True
        assert conf.FLASK_ENV == 'development'

    def test_production_config(self):
        from config import ProductionConfig
        conf = ProductionConfig()
        assert conf.DEBUG is False
        assert conf.FLASK_ENV == 'production'

    def test_config_dict(self):
        from config import config, DevelopmentConfig
        assert 'development' in config
        assert 'production' in config
        assert 'testing' in config
        assert config['default'] == DevelopmentConfig

class TestDatabase:
    def test_init_db(self):
        with patch('database.db.Base.metadata.create_all') as mock_create:
            from database.db import init_db, engine
            init_db()
            mock_create.assert_called_once_with(bind=engine)

    def test_get_db_session(self):
        from database.db import get_db_session
        session = get_db_session()
        assert session is not None
        session.close()

class TestSeedData:
    @patch('seed_data.get_db_session')
    def test_seed_exercises_already_exist(self, mock_db):
        mock_session = MagicMock()
        mock_session.query.return_value.first.return_value = MagicMock()
        mock_db.return_value = mock_session
        
        from seed_data import seed_exercises
        seed_exercises()
        
        mock_session.add.assert_not_called()

    @patch('seed_data.get_db_session')
    def test_seed_exercises_new(self, mock_db):
        mock_session = MagicMock()
        mock_session.query.return_value.first.return_value = None
        mock_db.return_value = mock_session
        
        from seed_data import seed_exercises
        seed_exercises()
        
        assert mock_session.add.called
        mock_session.commit.assert_called()

    @patch('seed_data.seed_admin_user')
    @patch('seed_data.seed_exercises')
    def test_seed_all(self, mock_exercises, mock_admin):
        from seed_data import seed_all
        seed_all()
        
        mock_admin.assert_called_once()
        mock_exercises.assert_called_once()

class TestApp:
    @patch('app.init_db')
    @patch('database.db.create_engine')
    def test_app_initialization(self, mock_engine, mock_init_db):
        mock_engine.return_value = MagicMock()
        
        import importlib
        import app as app_module
        importlib.reload(app_module)
        
        assert app_module.app is not None

    @patch('database.db.create_engine')
    def test_app_blueprints_registered(self, mock_engine):
        mock_engine.return_value = MagicMock()
        
        from app import app
        
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'code' in blueprint_names
        assert 'ai_assistant' in blueprint_names
        assert 'exercises' in blueprint_names
        assert 'attempts' in blueprint_names
        assert 'users' in blueprint_names