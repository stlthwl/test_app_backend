import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv('DB_USER')    # "admin"
    POSTGRES_PASSWORD: str = os.getenv('DB_PASSWORD')    # "password"
    POSTGRES_DB: str = os.getenv('DB_NAME')    # "postgrestest"
    POSTGRES_HOST: str = os.getenv('DB_HOST')    # "localhost"
    POSTGRES_PORT: str = os.getenv('DB_PORT')    # "5446"

    class Config:
        env_file_encoding = 'utf-8'


settings = Settings()


