from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from settings import settings
from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

class Development:
    """
    Development environment configuration.

    Description:
    Configuration settings for the development environment.

    Parameters:
    None

    Return:
    None
    """
    SQLALCHEMY_DATABASE_URI = settings.database_uri
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class Testing:
    """
    Testing environment configuration.

    Description:
    Configuration settings for the testing environment.

    Parameters:
    None

    Return:
    None
    """
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.sqlite3"
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class Production:
    """
    Production environment configuration.

    Description:
    Configuration settings for the production environment.

    Parameters:
    None

    Return:
    None
    """
    SQLALCHEMY_DATABASE_URI = settings.database_uri
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

config_mode = {
    'debug': Development,
    'testing': Testing,
    'prod': Production
}

def create_app(mode='debug'):
    """
    Create and configure the Flask app.

    Description:
    This function creates a Flask application instance and configures it based on the specified mode.

    Parameters:
    mode (str): The mode in which the application should run (default is 'debug').

    Return:
    app (Flask): The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_mode[mode])

    # Configure email settings
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = settings.mail_port
    app.config['MAIL_USERNAME'] = settings.sender
    app.config['MAIL_PASSWORD'] = settings.mail_password
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    # Initialize database, migration, and mail extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Configure Celery settings
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
            broker_connection_retry_on_startup=True,
            redbeat_redis_url="redis://localhost:6379/0",
            redbeat_lock_key=None,
            enable_utc=True,
            beat_max_loop_interval=5,
            beat_scheduler='redbeat.schedulers.RedBeatScheduler'
        ),
    )

    return app
