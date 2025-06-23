import os
import requests
from flask import current_app

class SentryService:
    """
    Service for interacting with the Sentry API to fetch monitoring data.
    """
    @staticmethod
    def get_latest_issues(limit: int = 5):
        """
        Fetches the most recent, unresolved issues for the project from the Sentry API.
        """
        sentry_auth_token = os.environ.get('SENTRY_AUTH_TOKEN')
        org_slug = os.environ.get('SENTRY_ORGANIZATION_SLUG')
        project_slug = os.environ.get('SENTRY_PROJECT_SLUG')

        if not all([sentry_auth_token, org_slug, project_slug]):
            current_app.logger.warning("Sentry API credentials are not configured. Cannot fetch issues.")
            return []

        api_url = f"https://sentry.io/api/0/projects/{org_slug}/{project_slug}/issues/"
        
        headers = {
            "Authorization": f"Bearer {sentry_auth_token}"
        }
        
        params = {
            "query": "is:unresolved",
            "sort": "date",
            "limit": limit
        }

        try:
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            issues_data = response.json()
            
            # Simplify the data for the frontend
            formatted_issues = []
            for issue in issues_data:
                formatted_issues.append({
                    'id': issue.get('id'),
                    'title': issue.get('title'),
                    'culprit': issue.get('culprit'),
                    'level': issue.get('level'),
                    'count': issue.get('count'),
                    'permalink': issue.get('permalink'),
                    'lastSeen': issue.get('lastSeen')
                })
            return formatted_issues

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Failed to fetch issues from Sentry API: {e}")
            return [] # Return an empty list on failure to prevent frontend errors
        except Exception as e:
            current_app.logger.error(f"An unexpected error occurred while processing Sentry data: {e}")
            return []

