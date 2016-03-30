import flask
from flask.ext.sqlalchemy import SQLAlchemy,SignallingSession, SessionBase
from flask import current_app
from celery import Celery
from flask.ext.mail import Mail
from flask.ext.redis import Redis
from functools import wraps
import random
from flask.ext.session import Session
   
class FlaskCelery(Celery):

    def __init__(self, *args, **kwargs):

        super(FlaskCelery, self).__init__(*args, **kwargs)
        self.patch_task()
        self.app = None

        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def patch_task(self):
        TaskBase = self.Task
        _celery = self

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
                else:
                    with self.app.app_context():
                        return TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app):
        self.app = app
        self.config_from_object(app.config)

    ### Code is based on http://stackoverflow.com/questions/17979655/how-to-implement-autoretry-for-celery-tasks
    def task(self, *args_task, **opts_task):
        def real_decorator(func):
            sup = super(FlaskCelery, self).task

            @sup(*args_task, **opts_task)
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    func(*args, **kwargs)
                except opts_task.get('autoretry_on', Exception) as exc:
                    wrapper.retry(exc=exc, args=args, kwargs=kwargs,)
            return wrapper
        return real_decorator    


###-----------------Adding code from https://gist.github.com/alexmic/7857543 to make tests working--------------
class _SignallingSession(SignallingSession):
    """A subclass of `SignallingSession` that allows for `binds` to be specified
    in the `options` keyword arguments.

    """
    def __init__(self, db, autocommit=False, autoflush=True, **options):
        self.app = db.get_app()
        self._model_changes = {}
        self.emit_modification_signals = \
            self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS']

        bind = options.pop('bind', None)
        if bind is None:
            bind = db.engine

        binds = options.pop('binds', None)
        if binds is None:
            binds = db.get_binds(self.app)

        SessionBase.__init__(self,
                             autocommit=autocommit,
                             autoflush=autoflush,
                             bind=bind,
                             binds=binds,
                             **options)

class _SQLAlchemy(SQLAlchemy):
    """A subclass of `SQLAlchemy` that uses `_SignallingSession`."""
    def create_session(self, options):
        return _SignallingSession(self, **options)    

celery = FlaskCelery(__name__,broker='redis://localhost:6379/0')
db = _SQLAlchemy()
mail = Mail()
redis = Redis()
##not going to use server side sessions
#sess = Session()
