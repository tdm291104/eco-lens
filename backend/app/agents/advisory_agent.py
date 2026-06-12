"""
Advisory Agent (Groq Llama 4 Maverick cho guide/follow-up, Scout cho gợi ý).

Skills:
- generate_disposal_guide(category, location, rules) -> {steps[], tips[], warnings[]}
    Gọi Groq Maverick để tạo hướng dẫn xử lý rác step-by-step.
- answer_followup(question, scan_context) -> {answer, sources[]}
    Gọi Groq Maverick để trả lời câu hỏi follow-up dựa trên context scan.
- suggest_alternatives(item_description) -> {alternatives[], difficulty}
    Gọi Groq Scout để gợi ý cách upcycle / tái sử dụng.
"""

import json
from typing import Any

from app.agents.llm_helpers import call_text_json, language_directive
from app.harness.registry import SkillRegistry
from app.harness.skill import Skill


class GenerateDisposalGuideSkill(Skill):
    """Tạo hướng dẫn xử lý rác step-by-step dựa trên loại rác và quy định địa phương."""

    name = "generate_disposal_guide"
    description = "Tạo hướng dẫn xử lý rác step-by-step (Groq Llama 4 Maverick)"
    input_schema = {"category": "str", "location": "str", "rules": "dict", "lang": "str"}
    output_schema = {"steps": "list", "tips": "list", "warnings": "list"}

    PROMPT_TEMPLATE = (
        "Bạn là trợ lý hướng dẫn xử lý rác thải tại Việt Nam. Dựa trên thông tin sau:\n"
        "- Loại rác: {category}\n"
        "- Khu vực: {location}\n"
        "- Quy định địa phương: {rules}\n\n"
        "Hãy tạo hướng dẫn xử lý ngắn gọn, thực tế, và trả về JSON với đúng các field sau:\n"
        '{{"steps": ["<bước 1>", "<bước 2>", "<bước 3>"], '
        '"tips": ["<mẹo nhỏ hữu ích>"], '
        '"warnings": ["<lưu ý quan trọng cần tránh>"]}}\n'
        "{lang_directive} Mỗi bước/mẹo/lưu ý là một câu ngắn gọn. "
        "Chỉ trả về JSON, không thêm giải thích."
    )

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        lang = kwargs.get("lang", "vi")
        prompt = self.PROMPT_TEMPLATE.format(
            category=kwargs["category"],
            location=kwargs["location"],
            rules=json.dumps(kwargs["rules"], ensure_ascii=False),
            lang_directive=language_directive(lang),
        )
        result = call_text_json(prompt, task_type="heavy")
        return {
            "steps": result.get("steps", []),
            "tips": result.get("tips", []),
            "warnings": result.get("warnings", []),
        }

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        if lang == "en":
            return (
                f"Generated a {len(output.get('steps', []))}-step guide, "
                f"{len(output.get('warnings', []))} warning(s)"
            )
        return (
            f"Đã tạo hướng dẫn {len(output.get('steps', []))} bước, "
            f"{len(output.get('warnings', []))} lưu ý"
        )


class AnswerFollowupSkill(Skill):
    """Trả lời câu hỏi follow-up của người dùng dựa trên ngữ cảnh lần scan vừa rồi."""

    name = "answer_followup"
    description = "Trả lời câu hỏi follow-up dựa trên scan context (Groq Llama 4 Maverick)"
    input_schema = {"question": "str", "scan_context": "dict", "lang": "str"}
    output_schema = {"answer": "str", "sources": "list"}

    PROMPT_TEMPLATE = (
        "Bạn là trợ lý EcoLens, trả lời câu hỏi follow-up của người dùng về rác thải "
        "dựa trên kết quả phân tích ảnh vừa thực hiện.\n\n"
        "Ngữ cảnh lần scan vừa rồi (JSON): {scan_context}\n\n"
        'Câu hỏi của người dùng: "{question}"\n\n'
        "Hãy trả lời ngắn gọn, thân thiện, dựa trên ngữ cảnh trên. "
        "Trả về JSON với đúng các field sau:\n"
        '{{"answer": "<câu trả lời>", '
        '"sources": ["<phần ngữ cảnh đã dùng để trả lời, ví dụ: local_rules, disposal_guide>"]}}\n'
        "{lang_directive} Chỉ trả về JSON, không thêm giải thích."
    )

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        lang = kwargs.get("lang", "vi")
        prompt = self.PROMPT_TEMPLATE.format(
            scan_context=json.dumps(kwargs["scan_context"], ensure_ascii=False),
            question=kwargs["question"],
            lang_directive=language_directive(lang),
        )
        result = call_text_json(prompt, task_type="heavy")
        return {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
        }

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        return str(output.get("answer", ""))[:80]


class SuggestAlternativesSkill(Skill):
    """Gợi ý cách tái sử dụng / upcycle đồ vật."""

    name = "suggest_alternatives"
    description = "Gợi ý upcycle / tái sử dụng đồ vật (Groq Llama 4 Scout)"
    input_schema = {"item_description": "str"}
    output_schema = {"alternatives": "list", "difficulty": "str"}

    PROMPT_TEMPLATE = (
        "Bạn là trợ lý gợi ý tái sử dụng/upcycle đồ vật tại Việt Nam. "
        'Với vật thể: "{item_description}", hãy trả về JSON:\n'
        '{{"alternatives": ["<gợi ý cách tái sử dụng/upcycle, ngắn gọn>"], '
        '"difficulty": "<mức độ thực hiện: dễ / trung bình / khó>"}}\n'
        "Đưa ra 2-3 gợi ý, viết bằng tiếng Việt. Chỉ trả về JSON, không thêm giải thích."
    )

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        prompt = self.PROMPT_TEMPLATE.format(item_description=kwargs["item_description"])
        result = call_text_json(prompt, task_type="light")
        return {
            "alternatives": result.get("alternatives", []),
            "difficulty": result.get("difficulty", ""),
        }

    def summarize_output(self, output: dict[str, Any]) -> str:
        return f"{len(output.get('alternatives', []))} gợi ý — độ khó: {output.get('difficulty', '')}"


def register(registry: SkillRegistry) -> None:
    """Đăng ký toàn bộ skill của Advisory Agent vào registry."""
    registry.register(GenerateDisposalGuideSkill())
    registry.register(AnswerFollowupSkill())
    registry.register(SuggestAlternativesSkill())
