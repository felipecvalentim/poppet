"""Flask middleware definitions. This is also where template filters are defined.

To be imported by the application.current_app() factory.
"""

import locale
from logging import getLogger
import os

from celery.signals import task_failure, worker_process_init,task_postrun
from flask import current_app, render_template, request,url_for
from markupsafe import Markup

from unifispot.base.utils.email import send_exception
from unifispot.extensions import db,celery
from unifispot.models import User


##solution to start fresh flask-sqlalchemy session on each task https://gist.github.com/twolfson/a1b329e9353f9b575131
@task_postrun.connect
def handle_celery_postrun(retval=None, *args, **kwargs):
    """After each Celery task, teardown our db session"""
    if current_app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']:
        if not isinstance(retval, Exception):
            db.session.commit()
    # If we aren't in an eager request (i.e. Flask will perform teardown), then teardown
    if not current_app.config['CELERY_ALWAYS_EAGER']:
        db.session.remove()



# Send email when a Celery task raises an unhandled exception.
@task_failure.connect
def celery_error_handler(sender, exception, **_):
    exception_name = exception.__class__.__name__
    task_module = sender.name
    send_exception('{} exception in {}'.format(exception_name, task_module))


# Setup default error templates.
@current_app.errorhandler(401)
@current_app.errorhandler(403)
@current_app.errorhandler(404)
@current_app.errorhandler(400)
@current_app.errorhandler(500)
def error_handler(e):
    code = getattr(e, 'code', 500)  # If 500, e == the exception.
    if code == 500:
        # Send email to all ADMINS.
        exception_name = e.__class__.__name__
        view_module = request.endpoint
        send_exception('{} exception in {}'.format(exception_name, view_module))
    return render_template('errors/{}.html'.format(code)), code


# Template filters.
@current_app.template_filter()
def whitelist(value):
    """Whitelist specific HTML tags and strings.

    Positional arguments:
    value -- the string to perform the operation on.

    Returns:
    Markup() instance, indicating the string is safe.
    """
    translations = {
        '&amp;quot;': '&quot;',
        '&amp;#39;': '&#39;',
        '&amp;lsquo;': '&lsquo;',
        '&amp;nbsp;': '&nbsp;',
        '&lt;br&gt;': '<br>',
    }
    escaped = str(Markup.escape(value))  # Escapes everything.
    for k, v in translations.items():
        escaped = escaped.replace(k, v)  # Un-escape specific elements using str.replace.
    return Markup(escaped)  # Return as 'safe'.


@current_app.template_filter()
def dollar(value):
    """Formats the float value into two-decimal-points dollar amount.
    From http://flask.pocoo.org/docs/templating/

    Positional arguments:
    value -- the string representation of a float to perform the operation on.

    Returns:
    Dollar formatted string.
    """
    return locale.currency(float(value), grouping=True)


@current_app.template_filter()
def sum_key(value, key):
    """Sums up the numbers in a 'column' in a list of dictionaries or objects.

    Positional arguments:
    value -- list of dictionaries or objects to iterate through.

    Returns:
    Sum of the values.
    """
    values = [r.get(key, 0) if hasattr(r, 'get') else getattr(r, key, 0) for r in value]
    return sum(values)


@current_app.template_filter()
def max_key(value, key):
    """Returns the maximum value in a 'column' in a list of dictionaries or objects.

    Positional arguments:
    value -- list of dictionaries or objects to iterate through.

    Returns:
    Sum of the values.
    """
    values = [r.get(key, 0) if hasattr(r, 'get') else getattr(r, key, 0) for r in value]
    return max(values)


@current_app.template_filter()
def average_key(value, key):
    """Returns the average value in a 'column' in a list of dictionaries or objects.

    Positional arguments:
    value -- list of dictionaries or objects to iterate through.

    Returns:
    Sum of the values.
    """
    values = [r.get(key, 0) if hasattr(r, 'get') else getattr(r, key, 0) for r in value]
    return float(sum(values)) / (len(values) or float('nan'))


