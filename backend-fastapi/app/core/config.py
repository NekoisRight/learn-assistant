from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+asyncmy://learn_user:learn_pass_123@127.0.0.1:3306/learn_assistant?charset=utf8mb4"
    JWT_SECRET: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # 通用 LLM 配置，换平台只改 .env
    LLM_API_KEY: str = ""
    LLM_MODEL_ID: str = "deepseek-v4.1-flash-1017"
    # 为空时依次回退到 GLM_BASE_URL、DashScope 兼容地址
    LLM_BASE_URL: str = ""
    GLM_BASE_URL: str = ""
    # anthropic / openai；留空按 base_url 自动识别
    LLM_PROTOCOL: str = ""
    LLM_MAX_TOKENS: int = 4096

    # 兼容旧变量名，LLM_API_KEY 优先
    DASHSCOPE_API_KEY: str = ""
    GLM_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def llm_api_key(self) -> str:
        return self.LLM_API_KEY or self.GLM_API_KEY or self.DASHSCOPE_API_KEY

    @property
    def llm_base_url(self) -> str:
        return (
            self.LLM_BASE_URL
            or self.GLM_BASE_URL
            or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )


settings = Settings()