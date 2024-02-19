from celery import Celery, Task, shared_task
from . import create_app
from .utils import send_mail

def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

app = create_app()
c_app = celery_init_app(app)


@shared_task
def celery_send_email(username, email, token):
    send_mail(username, email, token)
    return "Mail sent successfully"