# coding=utf-8
"""
consloe 1:
    celery worker -A celery_app.celery --loglevel=info
console 2: 
    celery flower -A celery_app.celery --address=127.0.0.1 --port=5555
"""

import time
from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


from flask_app import app

celery = make_celery(app)


@celery.task
def background_task():
    from flask_app import socketio, namespace
    socketio.emit(
        'data', {'data': 'Task starting...'},
        namespace=namespace
    )
    time.sleep(3)
    socketio.emit(
        'data', {'data': 'Task complete!'},
        namespace=namespace
    )


@celery.task
def async_task():
    print('Async!')
    time.sleep(5)
