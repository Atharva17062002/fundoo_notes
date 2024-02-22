from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from settings import settings
from celery import Celery, Task

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = settings.mail_port
    app.config['MAIL_USERNAME'] = settings.sender
    app.config['MAIL_PASSWORD'] = settings.mail_password
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
            broker_connection_retry_on_startup=True,
            redbeat_redis_url = "redis://localhost:6379/0",
            redbeat_lock_key = None,
            enable_utc=True,
            beat_max_loop_interval=5,
            beat_scheduler='redbeat.schedulers.RedBeatScheduler'
        ),
    )

    return app

# app = create_app(__name__)

