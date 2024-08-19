from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import google.oauth2.credentials
from google.auth.transport.requests import Request


class GoogleOAuth2Authentication(BaseAuthentication):
    def authenticate(self, request):
        if 'credentials' not in request.session:
            return None

        credentials_dict = request.session.get('credentials')
        if not credentials_dict:
            raise AuthenticationFailed('Invalid credentials')

        credentials = google.oauth2.credentials.Credentials(**credentials_dict)

        if credentials.expired:
            if credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    # Save the refreshed credentials back to the session
                    request.session['credentials'] = self.credentials_to_dict(
                        credentials)
                    request.session.save()
                except Exception as e:
                    raise AuthenticationFailed(
                        f'Token refresh failed: {str(e)}')
            else:
                raise AuthenticationFailed('No refresh token available')

        return (None, None)

    def credentials_to_dict(self, credentials) -> dict:
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
