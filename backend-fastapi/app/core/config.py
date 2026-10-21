from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+asyncmy://learn_user:learn_pass_123@127.0.0.1:3306/learn_assistant?charset=utf8mb4"
    JWT_SECRET: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # 通用 LLM 配置（OpenAI 兼容协议），换平台只改 .env
    LLM_API_KEY: str = ""
    LLM_MODEL_ID: str = "qwen-plus"
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    # 兼容旧变量名，LLM_API_KEY 优先
    DASHSCOPE_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def llm_api_key(self) -> str:
        return self.LLM_API_KEY or self.DASHSCOPE_API_KEY


settings = Settings()
