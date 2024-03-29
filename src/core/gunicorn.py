"""Gunicorn settings."""
import multiprocessing
from typing import Any

bind = "0.0.0.0:8080"
workers = multiprocessing.cpu_count() * 2 + 1

worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 100
timeout = 1000
keepalive = 2

spew = False

max_requests = 2000
max_requests_jitter = 400


def worker_abort(worker: Any) -> None:
    """Хука, запускающаяся при завершении работы воркера сигналом ABRT."""
    worker.log.info("worker received SIGABRT signal")
