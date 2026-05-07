from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str # API_KEY
    model_name: str # Modelo grop => llama-3.3-70b-versatile

    class Config:
        env_file = ".env"

settings = Settings()