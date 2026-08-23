"""
GitHub OAuth service.
"""
from authlib.integrations.requests_client import OAuth2Session
from app.config import settings
from typing import Optional, Dict, Any


class GitHubOAuthService:
    """GitHub OAuth service."""

    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_API = "https://api.github.com/user"

    def __init__(self):
        self.client_id = settings.github_oauth_client_id
        self.client_secret = settings.github_oauth_client_secret
        self.redirect_uri = settings.github_oauth_redirect_uri

    def get_authorization_url(self, state: str) -> str:
        """Generate GitHub OAuth authorization URL."""
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri,
            state=state
        )
        authorization_url = oauth.create_authorization_url(
            self.GITHUB_AUTH_URL
        )
        return authorization_url

    def fetch_token(self, code: str) -> Dict[str, Any]:
        """Fetch access token from GitHub."""
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri
        )
        token = oauth.fetch_token(
            self.GITHUB_TOKEN_URL,
            client_secret=self.client_secret,
            code=code
        )
        return token

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from GitHub."""
        oauth = OAuth2Session(token={"access_token": access_token})
        response = oauth.get(self.GITHUB_USER_API)
        return response.json()
