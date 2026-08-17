import argparse

from app.db.session import SessionLocal
from app.models.entities import ChatSession, Document
from app.repositories import user_repo


def main() -> None:
    """把默认 local 用户（id=1）的会话与文档迁移到指定用户名。"""
    parser = argparse.ArgumentParser(description="迁移 local 用户数据")
    parser.add_argument("--username", required=True, help="目标用户名（需已注册）")
    args = parser.parse_args()

    with SessionLocal() as db:
        user = user_repo.get_user_by_username(db, args.username)
        if user is None:
            print("目标用户不存在，请先注册")
            return
        session_count = (
            db.query(ChatSession).filter_by(user_id=1).update({"user_id": user.id})
        )
        document_count = (
            db.query(Document).filter_by(user_id=1).update({"user_id": user.id})
        )
        db.commit()
        print(f"迁移完成：会话 {session_count} 个，文档 {document_count} 个")


if __name__ == "__main__":
    main()
