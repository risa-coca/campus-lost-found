from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 10080
    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""
    WECHAT_MOCK: bool = True
    PUBLIC_BASE_URL: str = "http://127.0.0.1:8000"
    
    # 补充新增的模板 ID 配置
    WECHAT_TEMPLATE_MATCH: str = ""
    WECHAT_TEMPLATE_CLAIM: str = ""

    ZHIPU_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()