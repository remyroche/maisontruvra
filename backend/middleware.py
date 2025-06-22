from functools import wraps
from flask import request, jsonify, g
# Assume 'logger' is a configured logging instance

def rbac_check(required_role):
    """
    Decorator to protect routes by checking for a specific role (e.g., 'admin').
    It assumes user information (like ID and role) is attached to Flask's
    global object 'g.user' by a preceding authentication middleware.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not g.user.get('id'):
                # This case handles unauthenticated users.
                return jsonify({'error': 'Authentication required.'}), 401

            if g.user.get('role') != required_role:
                # This case handles authenticated users with insufficient permissions.
                logger.warning({
                    'message': 'RBAC Access Denied',
                    'userId': g.user.get('id'),
                    'requiredRole': required_role,
                    'userRole': g.user.get('role'),
                    'endpoint': request.path
                })
                return jsonify({'error': 'Forbidden: Insufficient permissions.'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
