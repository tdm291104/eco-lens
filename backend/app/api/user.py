"""
GET /api/user/{user_id}/impact

- Nhận {lang?} từ query params
- Gọi skill get_user_impact (Scoring Agent) qua Harness Layer
- Trả về {total_co2, scans, rank} - tổng hợp tác động môi trường tích lũy
  của user, đọc từ SQLite
"""

from fastapi import APIRouter, Request

from app.harness.router import SkillRouter
from app.schemas.api_schemas import UserImpactResponse

router = APIRouter(prefix="/api", tags=["user"])


@router.get("/user/{user_id}/impact", response_model=UserImpactResponse)
def get_user_impact(user_id: str, request: Request, lang: str = "vi") -> UserImpactResponse:
    """Tổng hợp tác động môi trường tích lũy của một user."""
    skill_router = SkillRouter(request.app.state.registry)

    result = skill_router.call("get_user_impact", user_id=user_id, lang=lang)
    return UserImpactResponse(**result)
