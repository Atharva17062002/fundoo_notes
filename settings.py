from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra = 'ignore')

    sender: str
    mail_password:str
    database_uri: str
    mail_port: int
    user_uri: str
    notes_uri: str
    label_uri: str
    jwt_key: str
    jwt_algo: str
    redis_port: int 
    redis_host: str
    redis_db: int
    
settings = Settings()