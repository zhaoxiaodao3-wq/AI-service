from redis import Redis
from rq import Queue

from app.core.config import get_settings


def enqueue_document_task(task_id: int) -> None:
    """把文档处理任务放入 RQ 队列，worker 异步消费。"""
    s = get_settings()
    queue = Queue(s.rq_queue_name, connection=Redis.from_url(s.redis_url))
    queue.enqueue("app.services.document_processing.process_document_task", task_id)
