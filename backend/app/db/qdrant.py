from qdrant_client import QdrantClient

from app.core.config import get_settings

settings = get_settings()

# 向量配置：dimension 必须与 Embedding 模型输出维度一致，阶段 3 会按模型调整
DISTANCE = "Cosine"  # 余弦相似度，衡量语义相近程度
VECTOR_SIZE = 1536  # 当前预留维度


def get_qdrant_client() -> QdrantClient:
    """创建 Qdrant 客户端连接。

    客户端只是连接到 Docker 里的 Qdrant 服务，不持有数据；
    后续所有增删改查都通过这个客户端完成。
    """
    return QdrantClient(url=settings.qdrant_url)


def ensure_collections() -> list[str]:
    """幂等创建文档向量与记忆向量两个集合。

    幂等 = 重复执行结果一致：先查已存在集合，存在就跳过创建，
    避免重复调用时因集合已存在而报错。
    """
    client = get_qdrant_client()
    names = [settings.qdrant_collection_doc, settings.qdrant_collection_memory]
    # 把已存在的集合名收集成 set，用集合判断比逐个 in 列表更快
    existing = {c.name for c in client.get_collections().collections}
    for name in names:
        if name not in existing:
            # 新建集合时指定向量维度与距离算法
            client.create_collection(
                collection_name=name,
                vectors_config={
                    "size": VECTOR_SIZE,
                    "distance": DISTANCE,
                },
            )
    return names


def check_qdrant() -> bool:
    """探测 Qdrant 是否可连接：能列出集合即认为正常。"""
    try:
        get_qdrant_client().get_collections()
        return True
    except Exception:
        return False
