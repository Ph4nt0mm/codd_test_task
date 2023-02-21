from pathlib import Path

import dotenv
from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PG_HOST: str
    PG_PORT: int
    PG_USER: str
    PG_PASSWORD: str
    PG_DATABASE: str

    def pg_conn(self):
        return {
            'host': self.PG_HOST,
            'port': self.PG_PORT,
            'user': self.PG_USER,
            'password': self.PG_PASSWORD,
            'database': self.PG_DATABASE,
        }

    class Config:
        env_file = Path(BASE_DIR, 'settings', 'env')
        dotenv.load_dotenv(env_file)


settings = Settings()


TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': settings.pg_conn(),
        }
    },
    'apps': {
        'models': {
            'models': ['app.database', 'aerich.models'],
            'default_connection': 'default'
        }
    }
}
