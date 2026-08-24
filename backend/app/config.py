"""
Configuration for the FDE Vault Agent Platform backend.
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""

    # GitHub configuration
    github_repo_url: str = ""
    github_pat: str = ""  # Personal Access Token for prototype

    # LLM configuration
    llm_provider: str = "anthropic"  # anthropic or openai
    llm_api_key: str = ""  # LLM API key (separate from GitHub PAT)
    llm_model: str = "claude-haiku-4-5"  # Default model

    # Embedding configuration
    embedding_provider: str = "openai"
    embedding_api_key: str = ""  # Embedding API key (can be same as LLM)
    embedding_model: str = "text-embedding-3-small"  # Default embedding model

    # GitHub OAuth configuration
    github_oauth_client_id: str = ""
    github_oauth_client_secret: str = ""
    github_oauth_redirect_uri: str = "http://localhost:3000/auth/callback"

    # Vault configuration
    vault_path: Path = Path("./vault_clone")

    # Database configuration
    database_url: str = "sqlite:///./vault.db"

    # API configuration
    api_prefix: str = "/api/v1"
    debug: bool = False

    # CORS: comma-separated list of allowed frontend origins. Must be explicit
    # (not "*") because the API uses credentialed requests — browsers reject
    # "*" + credentials. Set to your Vercel URL in production, e.g.
    # CORS_ALLOW_ORIGINS="https://your-app.vercel.app,http://localhost:3000"
    cors_allow_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse the comma-separated CORS origins into a clean list."""
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]

    # Logging configuration
    log_level: str = "INFO"

    # Admin secret for generating read-only access links via the CLI script.
    # Set a strong random value in .env / Render. Empty disables generation.
    admin_secret: str = ""

    # Whether access cookies require HTTPS (set true in production).
    cookie_secure: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
