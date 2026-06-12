"""
SkillNormalizer - chuẩn hóa input/output cho skill.

- normalize_input(skill, raw_input): kiểm tra/convert raw_input theo
  skill.input_schema trước khi gọi execute()
- normalize_output(skill, raw_output): kiểm tra/convert raw_output theo
  skill.output_schema trước khi trả về Orchestrator

input_schema/output_schema có dạng {field_name: "str"|"int"|"float"|"bool"|"list"|"dict"}.
Field không có trong dữ liệu đầu vào sẽ được bỏ qua (không bắt buộc tất cả
field phải có mặt) - chỉ field nào có mặt mới được kiểm tra/convert kiểu.
"""

from typing import Any

_TYPE_MAP: dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
}


class SkillNormalizer:
    """Chuẩn hóa input/output của skill theo input_schema/output_schema."""

    def normalize_input(self, skill: Any, raw_input: dict[str, Any]) -> dict[str, Any]:
        return self._normalize(raw_input, skill.input_schema, f"input của skill '{skill.name}'")

    def normalize_output(self, skill: Any, raw_output: dict[str, Any]) -> dict[str, Any]:
        return self._normalize(raw_output, skill.output_schema, f"output của skill '{skill.name}'")

    def _normalize(self, data: dict[str, Any], schema: dict[str, str], context: str) -> dict[str, Any]:
        if not schema:
            return data

        normalized = dict(data)
        for field, type_name in schema.items():
            if field not in normalized or normalized[field] is None:
                continue

            expected_type = _TYPE_MAP.get(type_name)
            if expected_type is None:
                continue

            value = normalized[field]
            if isinstance(value, expected_type):
                continue

            try:
                normalized[field] = expected_type(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Field '{field}' trong {context} phải có kiểu '{type_name}', "
                    f"nhận được {type(value).__name__}"
                ) from exc

        return normalized
