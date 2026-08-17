from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import ok
from app.db.session import get_db
from app.services import stats_service

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """返回模型调用统计：次数、成功率、Token、按模型分组。"""
    return ok(stats_service.get_stats(db))
