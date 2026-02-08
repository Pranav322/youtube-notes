from functools import cached_property
from typing import Set
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./notes.db"  # Default to SQLite for local dev

    # Azure OpenAI Settings
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_DEPLOYMENT_NAME: str = "gpt-4o"

    # Admin IPs (comma-separated string)
    ADMIN_IPS: str = ""

    @cached_property
    def admin_ips_set(self) -> Set[str]:
        if not self.ADMIN_IPS:
            return set()
        return set(ip.strip() for ip in self.ADMIN_IPS.split(",") if ip.strip())

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
