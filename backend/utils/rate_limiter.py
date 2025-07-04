from typing import Dict, List, Set, Callable, Any, Union
import time
from collections import defaultdict
from flask import request, jsonify, Response
from functools import wraps
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    An in-memory rate limiter.

    NOTE: This implementation is not suitable for production environments that use
    multiple worker processes (like Gunicorn or uWSGI), as each worker would have
    its own separate rate-limiting state. For production, a shared store like Redis
    (as in the previous version) is recommended.
    """

    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Set[str] = set()

    def is_rate_limited(self, identifier: str, max_requests: int, window: int) -> bool:
        """
        Check if an identifier is rate limited.

        Args:
            identifier: The identifier to check (usually an IP address).
            max_requests: Maximum number of requests allowed in the time window.
            window: Time window in seconds.

        Returns:
            True if the identifier is rate limited, False otherwise.
        """
        now = time.time()

        # Clean old requests that are outside the current window
        self.requests[identifier] = [
            req_time
            for req_time in self.requests[identifier]
            if now - req_time < window
        ]

        # Check if the request count exceeds the maximum allowed
        if len(self.requests[identifier]) >= max_requests:
            return True

        # Record the current request timestamp
        self.requests[identifier].append(now)
        return False

    def __call__(self, limit: int, per: int) -> Callable:
        """
        Makes the instance callable and returns the actual decorator. This method
        is invoked when you use `@rate_limiter(limit=5, per=300)`.

        Args:
            limit: Maximum number of requests allowed. This maps to `max_requests`.
            per: The time window in seconds. This maps to `window`.

        Returns:
            The decorator function.
        """

        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args: Any, **kwargs: Any) -> Union[Response, tuple]:
                # In a production environment behind a proxy, use 'X-Forwarded-For'.
                identifier = request.headers.get("X-Forwarded-For", request.remote_addr)

                if self.is_rate_limited(identifier, max_requests=limit, window=per):
                    logger.warning(
                        f"Rate limit exceeded for IP: {identifier} on endpoint: {request.path}"
                    )
                    return jsonify(
                        {"error": "Rate limit exceeded. Please try again later."}
                    ), 429

                return f(*args, **kwargs)

            return decorated_function

        return decorator


# Create a single, importable instance of the RateLimiter
rate_limiter = RateLimiter()
