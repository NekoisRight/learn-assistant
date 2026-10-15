from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+asyncmy://learn_user:learn_pass_123@127.0.0.1:3306/learn_assistant?charset=utf8mb4"
    JWT_SECRET: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    DASHSCOPE_API_KEY: str = ""
    LLM_MODEL_ID: str = "qwen-plus"
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
