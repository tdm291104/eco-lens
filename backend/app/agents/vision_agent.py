"""
Vision Agent (Groq Llama 4 Maverick - vision).

Skills:
- analyze_image(base64_image) -> {description, objects[], confidence}
    Gọi Groq Maverick (vision) để mô tả chi tiết vật thể trong ảnh.
- detect_material(base64_image) -> {material, color, condition}
    Gọi Groq Maverick (vision) để nhận dạng chất liệu bề mặt.
- request_clarification(confidence_score) -> {needs_retry, reason}
    Logic thuần (không gọi LLM) - yêu cầu chụp lại ảnh nếu confidence thấp.
"""

from typing import Any

from app.agents.llm_helpers import call_vision_json, language_directive
from app.harness.registry import SkillRegistry
from app.harness.skill import Skill


class AnalyzeImageSkill(Skill):
    """Mô tả chi tiết vật thể rác trong ảnh."""

    name = "analyze_image"
    description = "Mô tả chi tiết vật thể trong ảnh (Groq Llama 4 Maverick - vision)"
    input_schema = {"base64_image": "str", "lang": "str"}
    output_schema = {"description": "str", "objects": "list", "confidence": "float"}

    PROMPT_TEMPLATE = (
        "Bạn là trợ lý phân loại rác thải. Hãy quan sát ảnh và trả về JSON với "
        "đúng các field sau:\n"
        '{{"description": "<mô tả ngắn vật thể chính trong ảnh>", '
        '"objects": ["<tên các vật thể nhận diện được>"], '
        '"confidence": <số thực 0-1, độ tin cậy của bạn>}}\n'
        "{lang_directive} Chỉ trả về JSON, không thêm giải thích."
    )

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        lang = kwargs.get("lang", "vi")
        prompt = self.PROMPT_TEMPLATE.format(lang_directive=language_directive(lang))
        result = call_vision_json(kwargs["base64_image"], prompt)
        return {
            "description": result.get("description", ""),
            "objects": result.get("objects", []),
            "confidence": float(result.get("confidence", 0.0)),
        }

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        return str(output.get("description", ""))[:80]


class DetectMaterialSkill(Skill):
    """Nhận dạng chất liệu, màu sắc và tình trạng bề mặt vật thể."""

    name = "detect_material"
    description = "Nhận dạng chất liệu bề mặt (Groq Llama 4 Maverick - vision)"
    input_schema = {"base64_image": "str"}
    output_schema = {"material": "str", "color": "str", "condition": "str"}

    PROMPT = (
        "Bạn là trợ lý phân loại rác thải. Hãy quan sát ảnh và trả về JSON với "
        "đúng các field sau:\n"
        '{"material": "<chất liệu chính, ví dụ: nhựa PET, thủy tinh, kim loại, giấy, hữu cơ>", '
        '"color": "<màu sắc chủ đạo>", '
        '"condition": "<tình trạng: còn mới / đã sử dụng / móp, vỡ...>"}\n'
        "Chỉ trả về JSON, không thêm giải thích."
    )

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        result = call_vision_json(kwargs["base64_image"], self.PROMPT)
        return {
            "material": result.get("material", ""),
            "color": result.get("color", ""),
            "condition": result.get("condition", ""),
        }

    def summarize_output(self, output: dict[str, Any]) -> str:
        return f"{output.get('material', '')} · {output.get('color', '')} · {output.get('condition', '')}"


class RequestClarificationSkill(Skill):
    """Yêu cầu chụp lại ảnh nếu độ tin cậy nhận diện thấp (logic thuần, không gọi LLM)."""

    name = "request_clarification"
    description = "Kiểm tra confidence và yêu cầu chụp lại ảnh nếu cần (logic thuần)"
    input_schema = {"confidence_score": "float"}
    output_schema = {"needs_retry": "bool", "reason": "str"}

    CONFIDENCE_THRESHOLD = 0.6

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        confidence_score = kwargs["confidence_score"]
        if confidence_score < self.CONFIDENCE_THRESHOLD:
            return {
                "needs_retry": True,
                "reason": (
                    f"Độ tin cậy nhận diện thấp ({confidence_score:.2f}). "
                    "Vui lòng chụp lại ảnh rõ hơn, đủ sáng và gần vật thể hơn."
                ),
            }
        return {
            "needs_retry": False,
            "reason": f"Độ tin cậy đủ cao ({confidence_score:.2f}), không cần chụp lại.",
        }

    def summarize_output(self, output: dict[str, Any]) -> str:
        return output["reason"]


def register(registry: SkillRegistry) -> None:
    """Đăng ký toàn bộ skill của Vision Agent vào registry."""
    registry.register(AnalyzeImageSkill())
    registry.register(DetectMaterialSkill())
    registry.register(RequestClarificationSkill())
