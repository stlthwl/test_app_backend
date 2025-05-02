import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv('DB_USER')
    POSTGRES_PASSWORD: str = os.getenv('DB_PASSWORD')
    POSTGRES_DB: str = os.getenv('DB_NAME')
    POSTGRES_HOST: str = os.getenv('DB_HOST')
    POSTGRES_PORT: str = os.getenv('DB_PORT')

    class Config:
        env_file_encoding = 'utf-8'


settings = Settings()


