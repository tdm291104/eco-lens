"""
GET /api/disposal-points

- Nhận {lat, lng, waste_type, lang?} từ query params
- Gọi skill find_disposal_points (Localization Agent) qua Harness Layer
- Trả về danh sách điểm thu gom gần nhất (tên, địa chỉ, khoảng cách, giờ mở)
  để hiển thị ở phần "Điểm thu gom gần nhất" trên frontend
"""

from fastapi import APIRouter, Request

from app.harness.router import SkillRouter
from app.schemas.api_schemas import DisposalPointsResponse

router = APIRouter(prefix="/api", tags=["localization"])


@router.get("/disposal-points", response_model=DisposalPointsResponse)
def get_disposal_points(
    lat: float, lng: float, waste_type: str, request: Request, lang: str = "vi"
) -> DisposalPointsResponse:
    """Tìm điểm thu gom gần nhất theo vị trí và loại rác."""
    skill_router = SkillRouter(request.app.state.registry)

    result = skill_router.call(
        "find_disposal_points", lat=lat, lng=lng, waste_type=waste_type, lang=lang
    )
    return DisposalPointsResponse(**result)
