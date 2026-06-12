"""
POST /api/scan

- Nhận ảnh (base64) từ client
- Chạy Orchestrator (LangGraph pipeline) qua Harness Layer
- Trả về:
    - kết quả phân loại (category, recyclable, hazardous, disposal guide,
      co2_saved, green_points, ...)
    - skill execution trace (danh sách các bước: tên skill, latency ms,
      output summary) lấy từ HarnessLogger để frontend hiển thị
      Skill Execution Trace UI
"""

from typing import Any

from fastapi import APIRouter, Request

from app.harness.router import SkillRouter
from app.orchestrator.graph import run_scan_pipeline
from app.schemas.api_schemas import ScanRequest, ScanResponse, ScanResult

router = APIRouter(prefix="/api", tags=["scan"])


@router.post("/scan", response_model=ScanResponse)
def scan(payload: ScanRequest, request: Request) -> ScanResponse:
    """Chạy pipeline scan đầy đủ và trả về kết quả + skill execution trace."""
    skill_router = SkillRouter(request.app.state.registry)

    initial_state: dict[str, Any] = {"base64_image": payload.base64_image}
    if payload.city:
        initial_state["city"] = payload.city
    if payload.user_id:
        initial_state["user_id"] = payload.user_id
    if payload.weight_g is not None:
        initial_state["weight_g"] = payload.weight_g
    if payload.lang:
        initial_state["lang"] = payload.lang

    final_state = run_scan_pipeline(skill_router, **initial_state)

    return ScanResponse(
        result=ScanResult(**final_state),
        trace=skill_router.logger.get_trace(),
    )
