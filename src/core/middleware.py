import logging
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, _StreamingResponse

log = logging.getLogger(__name__)


class LoggerMiddleware(BaseHTTPMiddleware):
    """Мидлварина для логирования."""

    async def dispatch(
        self, request: Request, call_next: Request
    ) -> _StreamingResponse:
        """Логирование запросов."""
        request_id = str(uuid.uuid4())
        request_body = {"status": "REQUEST_START", "request_id": request_id}
        response_body = {"status": "REQUEST_END", "request_id": request_id}
        log.info(msg="", extra=request_body)
        try:
            response = await call_next(request)
            response_body["status_code"] = response.status_code
        except Exception as exc:
            error_msg = exc
            response_body["error_msg"] = str(error_msg)
        log.info(msg="", extra=response_body)
        return response
