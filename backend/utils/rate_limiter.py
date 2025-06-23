
import time
from collections import defaultdict
from flask import request, jsonify
from functools import wraps

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = set()
    
    def is_rate_limited(self, identifier, max_requests=100, window=3600):
        """Check if an identifier is rate limited."""
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
    
    def rate_limit(self, max_requests=100, window=3600):
        """Decorator for rate limiting routes."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                identifier = request.remote_addr
                
                if self.is_rate_limited(identifier, max_requests, window):
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

# Global rate limiter instance
rate_limiter = RateLimiter()
