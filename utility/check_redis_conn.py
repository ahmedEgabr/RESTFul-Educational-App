from redis import Redis
from django.conf import settings

def check_redis_connection():
    redis_host = settings.BROKER_URL.split(":")[1].split("//")[1]
    redis = Redis(redis_host, socket_connect_timeout=1) # short timeout for the test

    try:
        redis.ping()
    except:
        return False
    else:
        return True
