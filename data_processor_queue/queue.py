from rq import Queue
from rq_scheduler import Scheduler
from redis import Redis

from settings import platform_settings

settings = platform_settings()

redis_conn = Redis(host=settings.redis_host, password=settings.redis_password)
dpq = Queue("platform_default", connection=redis_conn)
notification_queue = Queue("platform_notification", connection=redis_conn)
scheduler = Scheduler("platform_default", connection=redis_conn)
