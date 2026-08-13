from app.db.qdrant import ensure_collections


def main() -> None:
    names = ensure_collections()
    print("Qdrant Collections 就绪:", ", ".join(names))


if __name__ == "__main__":
    main()
