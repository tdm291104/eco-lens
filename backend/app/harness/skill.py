"""
Skill base class - interface chuẩn mà mọi skill phải implement.

Mỗi skill subclass khai báo:
- name: str            -> tên skill, unique trong SkillRegistry
- description: str     -> mô tả để Orchestrator/LLM hiểu khi nào dùng skill này
- input_schema: dict    -> schema của input, dạng {field_name: "str"|"int"|"float"|"bool"|"list"|"dict"}
- output_schema: dict   -> schema của output, cùng dạng với input_schema
- execute(self, **kwargs) -> dict  -> logic chính của skill

Orchestrator chỉ biết tên skill, không biết agent nào implement nó.
"""

from abc import ABC, abstractmethod
from typing import Any


class Skill(ABC):
    """Base class cho mọi skill trong Skill Registry."""

    name: str = ""
    description: str = ""
    input_schema: dict[str, str] = {}
    output_schema: dict[str, str] = {}

    @abstractmethod
    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Thực thi skill, trả về dict tuân theo output_schema."""
        raise NotImplementedError

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        """
        Tóm tắt ngắn output cho Skill Execution Trace.

        `lang` ("vi" | "en") cho biết ngôn ngữ hiển thị mong muốn của summary.
        Mặc định nối các field lại thành một chuỗi gọn. Skill nên override
        để trả về tóm tắt dễ hiểu hơn, theo `lang`.
        """
        return ", ".join(f"{key}={value!r}" for key, value in output.items())
