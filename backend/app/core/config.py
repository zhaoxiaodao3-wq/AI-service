from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置类：从 .env 读取所有可配置项。

    继承 BaseSettings 后，pydantic-settings 会自动把环境变量映射到同名属性，
    例如 .env 里的 DATABASE_URL 会填到 database_url 字段。
    """

    # 告诉 pydantic：配置来源是 .env 文件，编码 utf-8，多余字段忽略不报错
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用基本信息
    app_name: str = "aigc-backend"
    app_env: str = "development"
    # 敏感字段加密密钥（Fernet key）；生产环境必须换成自己的随机值
    secret_key: str = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="

    # 数据库连接串：格式 postgresql+psycopg://用户:密码@主机:端口/库名
    database_url: str = (
        "postgresql+psycopg://aigc_user:change_me@localhost:5432/aigc_chat"
    )

    # Qdrant 向量库地址与两个集合名称
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_doc: str = "document_vectors"
    qdrant_collection_memory: str = "memory_vectors"

    # LLM 配置预留：阶段 0 不调用，阶段 1 开始使用
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""
    llm_proxy_base_url: str = ""
    llm_proxy_api_key: str = ""

    # 可用模型清单（阶段 2 后改为数据库管理，当前静态配置）
    models: list[str] = [
        "glm-4-flash",
        "gpt-4o",
        "gpt-4o-mini",
        "deepseek-chat",
        "claude-3-5-sonnet-20241022",
    ]
    # 短期上下文 token 上限：超过后删除最早消息，防止上下文溢出
    max_context_tokens: int = 4000

    # Embedding / RAG 配置：阶段 3 使用
    embedding_mode: str = "api"  # api=真实模型；local=开发期本地哈希向量
    embedding_model: str = "embedding-2"
    embedding_api_key: str = ""
    embedding_base_url: str = ""
    embedding_dimensions: int = 1024
    chunk_size: int = 500
    chunk_overlap: int = 50
    rag_top_k: int = 3
    rag_score_threshold: float = 0.35

    # 长期记忆：阶段 4 使用
    memory_enabled: bool = True
    memory_top_k: int = 3
    memory_score_threshold: float = 0.35

    # 工程化：阶段 5 使用
    llm_retry_count: int = 1
    rate_limit_per_minute: int = 30


@lru_cache
def get_settings() -> Settings:
    """获取全局配置单例。

    lru_cache 让 Settings 只创建一次并缓存，避免每个请求都重新读 .env 文件，
    提升性能；后续代码统一通过 get_settings() 取配置。
    """
    return Settings()
