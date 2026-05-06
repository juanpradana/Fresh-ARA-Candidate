import os


class Settings:
    @property
    def app_db_path(self) -> str:
        return os.getenv("APP_DB_PATH", "./data/fresh_ara.sqlite")


settings = Settings()
