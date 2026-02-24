from pydantic import BaseSettings

class Settings(BaseSettings):
    api_key: str
    pdf_upload_path: str
    vector_db_url: str
    logging_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()