import redis
from rq import Queue, Worker

from app.core.config import get_settings
from app.models import entities  # noqa: F401  确保表定义加载


def main() -> None:
    s = get_settings()
    connection = redis.Redis.from_url(s.redis_url)
    queue = Queue(s.rq_queue_name, connection=connection)
    Worker([queue]).work()


if __name__ == "__main__":
    main()
