from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    PROJECT_NAME: str = "LLM Reliability Platform"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = (
        "Production-ready platform for evaluating and improving LLM reliability."
    )
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()