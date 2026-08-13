from app.db.qdrant import ensure_collections


def main() -> None:
    """脚本入口：确保 document_vectors 与 memory_vectors 两个集合存在。"""
    names = ensure_collections()
    print("Qdrant Collections 就绪:", ", ".join(names))


if __name__ == "__main__":
    # 只有直接运行本脚本时才执行，被 import 时不执行
    main()
