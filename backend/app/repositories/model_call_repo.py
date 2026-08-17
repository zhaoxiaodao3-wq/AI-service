from sqlalchemy.orm import Session

from app.models.entities import ModelCall


def create_model_call(
    db: Session,
    session_id: int | None,
    model: str,
    success: bool,
    token_count: int | None,
    duration_ms: int,
) -> ModelCall:
    call = ModelCall(
        session_id=session_id,
        model=model,
        success=success,
        token_count=token_count,
        duration_ms=duration_ms,
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return call
