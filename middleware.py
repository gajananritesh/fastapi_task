# middleware.py
import logging
import sys
from datetime import datetime, timezone
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware



# Configure the logger format
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s | %(levelname)-7s | %(message)s", handlers=[
    logging.StreamHandler(sys.stdout),
    # logging.FileHandler("api_requests.log")  # Uncomment to log directly to a file
    ])
logger = logging.getLogger("api_access")


class LoggingMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    # 1. Capture or generate request_id (reuse if client sent one)
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Store request_id in request.state so routes can access it if needed
    request.state.request_id = request_id

    # 2. Extract request details
    method = request.method
    path = request.url.path
    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()

    try:
      # 3. Process the request
      response = await call_next(request)
      status_code = response.status_code
    except Exception as exc:
      # Capture unhandled 500 errors
      status_code = 500
      execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
      logger.error(
          f"request_id={request_id} | method={method} | path={path} | "
          f"status={status_code} | timestamp={timestamp} | "
          f"duration={execution_time_ms}ms | error={str(exc)}"
      )
      raise exc

    # 4. Calculate total response time
    execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # 5. Log the metrics
    logger.info(f"request_id={request_id} | method={method} | path={path} | status={status_code} | timestamp={timestamp} | duration={execution_time_ms}ms |")

    # 6. Append headers to the outgoing response
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{execution_time_ms}ms"

    return response