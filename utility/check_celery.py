from alteby.celery import app

def check_celery_workers():
    result = app.control.broadcast('ping', reply=True, limit=1)
    return bool(result)  # True if at least one result
