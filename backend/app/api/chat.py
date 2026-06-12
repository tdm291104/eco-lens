"""
POST /api/chat

- Nhận {question, scan_context} từ client
- Gọi skill answer_followup (Advisory Agent) qua Harness Layer
- Trả về {answer, sources[]} để hiển thị trong ChatPanel của frontend
"""

from fastapi import APIRouter, Request

from app.harness.router import SkillRouter
from app.schemas.api_schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    """Trả lời câu hỏi follow-up dựa trên scan_context vừa phân tích."""
    skill_router = SkillRouter(request.app.state.registry)

    result = skill_router.call(
        "answer_followup",
        question=payload.question,
        scan_context=payload.scan_context,
        lang=payload.lang or "vi",
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        trace=skill_router.logger.get_trace(),
    )
