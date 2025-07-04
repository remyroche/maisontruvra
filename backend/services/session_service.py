"""
Service layer for managing user sessions.
This service will interact with the session storage backend (e.g., Redis)
to provide functionalities like listing and revoking active sessions.
"""

from flask import current_app
from ...extensions import db
from ...models import User, PersistentSession


class SessionService:
    """
    Provides methods for managing user sessions.

    NOTE: This implementation assumes you are storing session information in your main database.
    For high-performance applications, this data is often stored in a cache like Redis.
    The logic would need to be adapted for a Redis-based session store.
    """

    @staticmethod
    def get_all_active_sessions(page=1, per_page=20):
        """
        Retrieves a paginated list of all active user sessions.
        """
        current_app.logger.info("Fetching all active sessions.")

        # This query assumes a 'PersistentSession' model that tracks active sessions.
        # It joins with the User model to get user details.
        sessions_page = (
            PersistentSession.query.join(User)
            .filter(PersistentSession.is_active)
            .order_by(PersistentSession.last_seen.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return sessions_page

    @staticmethod
    def terminate_session(session_id: str, performing_user_id: int):
        """
        Terminates a specific user db.session.

        :param session_id: The ID of the session to terminate.
        :param performing_user_id: The ID of the admin performing the action (for auditing).
        :return: True if the session was terminated, False otherwise.
        """
        current_app.logger.info(
            f"Admin {performing_user_id} is attempting to terminate session {session_id}."
        )

        session_to_terminate = PersistentSession.query.get(session_id)

        if not session_to_terminate:
            current_app.logger.warning(
                f"Attempted to terminate non-existent session ID: {session_id}"
            )
            return False

        if not session_to_terminate.is_active:
            current_app.logger.info(f"Session {session_id} is already inactive.")
            return True  # The desired state is achieved

        # In a real implementation, you would invalidate the session in your store (e.g., Redis or Flask-Session).
        # For this example, we'll mark it as inactive in the database.
        session_to_terminate.is_active = False
        db.session.commit()

        current_app.logger.info(
            f"Successfully terminated session {session_id} by admin {performing_user_id}."
        )
        return True
