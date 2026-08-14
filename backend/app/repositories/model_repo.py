from sqlalchemy.orm import Session

from app.models.entities import AiModel


def list_enabled_models(db: Session) -> list[AiModel]:
    """返回启用状态的模型，按权重升序。"""
    return (
        db.query(AiModel)
        .filter_by(enabled=True)
        .order_by(AiModel.weight.asc())
        .all()
    )


def get_model_by_name(db: Session, name: str) -> AiModel | None:
    return db.query(AiModel).filter_by(name=name).first()
