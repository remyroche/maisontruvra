from functools import wraps
from flask import request
from flask_login import current_user
from ..services.audit_log_service import AuditLogService

def log_admin_action(action: str, target_type: str = None):
    """
    A decorator to automatically log admin actions, including the "before" and
    "after" state of data for modifications.

    Args:
        action (str): A description of the action being performed (e.g., "Viewed Page", "Updated Product").
        target_type (str): The type of object being acted upon (e.g., 'Product', 'User').
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # For GET requests, we just log the viewing action.
            if request.method == 'GET':
                AuditLogService.log(
                    admin_user_id=current_user.id,
                    action=action,
                    target_type=target_type
                )
                return f(*args, **kwargs)

            # For PUT, POST, DELETE, we log more details.
            details = {'request_data': request.get_json(silent=True)}
            
            # --- Capture 'before' state for PUT/DELETE ---
            # This requires the endpoint to have a parameter matching the target_type,
            # e.g., @log_admin_action('Update Product', 'product') on a route /product/<int:product_id>
            target_id = kwargs.get(f'{target_type.lower()}_id') if target_type else None
            if target_id and (request.method in ['PUT', 'DELETE']):
                # A helper function would be needed to get the object before the change
                # For now, we will log the ID of the object being changed.
                details['before_state'] = {'id': target_id, 'message': 'State before change not captured in this version.'}


            # Execute the actual endpoint function
            response = f(*args, **kwargs)
            
            
            # --- Capture 'after' state ---
            if response and isinstance(response, tuple) and response[0].is_json:
                details['after_state'] = response[0].get_json()

            AuditLogService.log(
                admin_user_id=current_user.id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                details=details
            )

            return response
        return decorated_function
    return decorator
