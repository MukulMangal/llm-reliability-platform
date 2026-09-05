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

    GEMINI_API_KEY: str

    # Razorpay Test Mode configuration
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    RAZORPAY_BASE_URL: str = "https://api.razorpay.com/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()