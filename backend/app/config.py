from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    port: int = 8000
    frontend_url: str = "http://localhost:3000"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    serpapi_key: str = ""
    playwright_headless: bool = True
    playwright_timeout_ms: int = 30000
    analysis_model: str = "gpt-4o"

    model_config = {"env_file": ".env"}


settings = Settings()
