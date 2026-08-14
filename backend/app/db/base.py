from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类：所有 ORM 实体都继承它。"""
