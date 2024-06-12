from pydantic_settings import BaseSettings, SettingsConfigDict

from app.logs.logger import get_logger


class Settings(BaseSettings):

    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    CURRENT_TOKEN: str = ""
    HIKVISION_URL: str

    model_config = SettingsConfigDict(env_file="app/.env")

    APP_KEY: str
    SECRET_KEY: str

    KEY: str
    ALGORITHM: str

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()

logger = get_logger(__name__)
logger.info(f"Данные окружения имортированы из '{settings['env_file']}'")
print(settings.model_config)
