from rest_framework.permissions import BasePermission
import google.oauth2.credentials
from google.auth.transport.requests import Request


# Custom permission
class HasValidGoogleOAuth2Credentials(BasePermission):
    def has_permission(self, request, view):
        if 'credentials' not in request.session:
            return False

        credentials_dict = request.session.get('credentials')
        if not credentials_dict:
            return False

        credentials = google.oauth2.credentials.Credentials(**credentials_dict)

        if credentials.expired:
            if credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    # Save the refreshed credentials back to the session
                    request.session['credentials'] = self.credentials_to_dict(
                        credentials)
                    request.session.save()
                except Exception:
                    return False
            else:
                return False

        return True

    def credentials_to_dict(self, credentials) -> dict:
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
