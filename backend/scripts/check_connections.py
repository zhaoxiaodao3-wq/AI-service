from app.db.qdrant import check_qdrant
from app.db.session import check_database


def main() -> None:
    print(f"PostgreSQL: {'ok' if check_database() else 'error'}")
    print(f"Qdrant: {'ok' if check_qdrant() else 'error'}")


if __name__ == "__main__":
    main()
