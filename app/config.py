from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    default_fee_rate: float = 0.001
    min_net_spread_pct: float = 0.15
    request_timeout_seconds: float = 8.0
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
