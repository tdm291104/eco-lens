"""
Classification Agent (Groq Llama 4 Scout).

Skills:
- classify_waste_type(description, material) -> {category, subcategory, recyclable}
    Gọi Groq Scout để phân loại vật thể vào nhóm rác chính.
- lookup_material_code(material_name) -> {code, full_name, recyclability}
    Gọi Groq Scout để tra mã vật liệu chuẩn (PET #1, HDPE #2, ...).
- flag_hazardous(category) -> {is_hazardous, warning_level, reason}
    Gọi Groq Scout để cảnh báo rác nguy hại.
"""

from typing import Any

from app.agents.llm_helpers import call_text_json, language_directive
from app.harness.registry import SkillRegistry
from app.harness.skill import Skill


class ClassifyWasteTypeSkill(Skill):
    """Phân loại vật thể vào nhóm rác chính dựa trên mô tả và chất liệu."""

    name = "classify_waste_type"
    description = "Phân loại nhóm rác từ mô tả + chất liệu (Groq Llama 4 Scout)"
    input_schema = {"description": "str", "material": "str", "lang": "str"}
    output_schema = {"category": "str", "subcategory": "str", "recyclable": "bool"}

    PROMPT_TEMPLATE = (
        "Bạn là trợ lý phân loại rác thải tại Việt Nam. Dựa trên thông tin sau:\n"
        "- Mô tả vật thể: {description}\n"
        "- Chất liệu: {material}\n\n"
        "Hãy trả về JSON với đúng các field sau:\n"
        '{{"category": "<PHẢI là một trong 4 giá trị tiếng Việt cố định sau, dùng làm mã '
        'nội bộ, giữ nguyên không dịch: Rác tái chế / Rác hữu cơ / Rác nguy hại / Rác thông thường>", '
        '"subcategory": "<phân loại cụ thể hơn, ví dụ: Nhựa PET #1>", '
        '"recyclable": <true hoặc false>}}\n'
        "{lang_directive} (field category vẫn giữ đúng 1 trong 4 giá trị tiếng Việt cố định ở trên)\n"
        "Chỉ trả về JSON, không thêm giải thích."
    )

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        lang = kwargs.get("lang", "vi")
        prompt = self.PROMPT_TEMPLATE.format(
            description=kwargs["description"],
            material=kwargs["material"],
            lang_directive=language_directive(lang),
        )
        result = call_text_json(prompt, task_type="light")
        return {
            "category": result.get("category", ""),
            "subcategory": result.get("subcategory", ""),
            "recyclable": bool(result.get("recyclable", False)),
        }

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        arrow = "->" if lang == "en" else "→"
        return f"{output.get('category', '')} {arrow} {output.get('subcategory', '')}"


class LookupMaterialCodeSkill(Skill):
    """Tra mã vật liệu tái chế chuẩn (Resin Identification Code) cho chất liệu."""

    name = "lookup_material_code"
    description = "Tra mã vật liệu chuẩn cho chất liệu (Groq Llama 4 Scout)"
    input_schema = {"material_name": "str"}
    output_schema = {"code": "str", "full_name": "str", "recyclability": "str"}

    PROMPT_TEMPLATE = (
        "Bạn là cơ sở dữ liệu mã vật liệu tái chế chuẩn quốc tế (Resin Identification Code). "
        'Với chất liệu: "{material_name}", hãy trả về JSON:\n'
        '{{"code": "<mã vật liệu, ví dụ: Nhựa PET #1, HDPE #2, PVC #3, LDPE #4, PP #5, PS #6, '
        'Other #7, hoặc \\"Không có mã nhựa\\" nếu không phải nhựa>", '
        '"full_name": "<tên đầy đủ chất liệu>", '
        '"recyclability": "<mô tả khả năng tái chế, ngắn gọn, tiếng Việt>"}}\n'
        "Chỉ trả về JSON, không thêm giải thích."
    )

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        prompt = self.PROMPT_TEMPLATE.format(material_name=kwargs["material_name"])
        result = call_text_json(prompt, task_type="light")
        return {
            "code": result.get("code", ""),
            "full_name": result.get("full_name", ""),
            "recyclability": result.get("recyclability", ""),
        }

    def summarize_output(self, output: dict[str, Any]) -> str:
        return f"{output.get('code', '')} — {output.get('full_name', '')}"


class FlagHazardousSkill(Skill):
    """Đánh giá mức độ nguy hại của một nhóm rác."""

    name = "flag_hazardous"
    description = "Cảnh báo rác nguy hại theo nhóm rác (Groq Llama 4 Scout)"
    input_schema = {"category": "str", "lang": "str"}
    output_schema = {"is_hazardous": "bool", "warning_level": "str", "reason": "str"}

    PROMPT_TEMPLATE = (
        "Bạn là trợ lý cảnh báo rác thải nguy hại tại Việt Nam. "
        'Với nhóm rác: "{category}", hãy đánh giá và trả về JSON:\n'
        '{{"is_hazardous": <true hoặc false>, '
        '"warning_level": "<mức cảnh báo: none / low / medium / high>", '
        '"reason": "<lý do ngắn gọn>"}}\n'
        "{lang_directive} Chỉ trả về JSON, không thêm giải thích."
    )

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        lang = kwargs.get("lang", "vi")
        prompt = self.PROMPT_TEMPLATE.format(
            category=kwargs["category"], lang_directive=language_directive(lang)
        )
        result = call_text_json(prompt, task_type="light")
        return {
            "is_hazardous": bool(result.get("is_hazardous", False)),
            "warning_level": result.get("warning_level", "none"),
            "reason": result.get("reason", ""),
        }

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        return output.get("reason", "")


def register(registry: SkillRegistry) -> None:
    """Đăng ký toàn bộ skill của Classification Agent vào registry."""
    registry.register(ClassifyWasteTypeSkill())
    registry.register(LookupMaterialCodeSkill())
    registry.register(FlagHazardousSkill())
