import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB')
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST')
    POSTGRES_PORT: str = os.getenv('POSTGRES_PORT')
    AWS_ACCESS_KEY_ID: str = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY: str = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET_NAME: str = os.getenv('AWS_S3_BUCKET_NAME')
    AWS_S3_REGION: str = os.getenv('AWS_S3_REGION')

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True


settings = Settings()
