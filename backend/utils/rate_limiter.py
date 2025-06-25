
from typing import Dict, List, Set, Callable, Any, Union
import time
from collections import defaultdict
from flask import request, jsonify, Response
from functools import wraps

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Set[str] = set()
    
    def is_rate_limited(self, identifier: str, max_requests: int = 100, window: int = 3600) -> bool:
        """
        Check if an identifier is rate limited.
        
        Args:
            identifier: The identifier to check (usually an IP address)
            max_requests: Maximum number of requests allowed in the time window
            window: Time window in seconds
            
        Returns:
            True if the identifier is rate limited, False otherwise
        """
        now = time.time()
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] 
            if now - req_time < window
        ]
        
        # Check if rate limited
        if len(self.requests[identifier]) >= max_requests:
            return True
        
        # Add current request
        self.requests[identifier].append(now)
        return False
    
    def rate_limit(self, max_requests: int = 100, window: int = 3600) -> Callable:
        """
        Decorator for rate limiting routes.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            window: Time window in seconds
            
        Returns:
            Decorator function
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args: Any, **kwargs: Any) -> Union[Response, tuple]:
                identifier = request.remote_addr
                
                if self.is_rate_limited(identifier, max_requests, window):
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

# Global rate limiter instance
rate_limiter = RateLimiter()
