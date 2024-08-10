from functools import lru_cache

import yaml
from pydantic_settings import BaseSettings

from line_provider.constants import SETTINGS_PATH


class PostgresSettings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    max_overflow: int
    pool_size: int
    db_user: str
    db_password: str

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class LineProviderSettings(BaseSettings):
    title: str
    host: str
    port: int


class RabbitSettings(BaseSettings):
    rabbit_host: str
    rabbit_vhost: str
    rabbit_user: str
    rabbit_pass: str

    @property
    def rabbit_url(self) -> str:
        return f"amqp://{self.rabbit_user}:{self.rabbit_pass}@{self.rabbit_host}/{self.rabbit_vhost}"


class Settings(BaseSettings):
    line_provider: LineProviderSettings
    postgres: PostgresSettings
    rabbit: RabbitSettings


@lru_cache
def get_settings() -> Settings:
    with open(SETTINGS_PATH) as file:
        settings = Settings.model_validate(yaml.load(file, Loader=yaml.FullLoader))

    return settings
