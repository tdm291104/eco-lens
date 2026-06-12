"""
SkillRouter - định tuyến lời gọi skill.

call(skill_name, **params):
    1. Tra SkillRegistry để lấy Skill instance theo skill_name
    2. Dùng SkillNormalizer để chuẩn hóa input theo input_schema
    3. Gọi skill.execute(**normalized_input), retry nếu lỗi (tối đa max_retries)
    4. Dùng SkillNormalizer để chuẩn hóa output theo output_schema
    5. Ghi log qua HarnessLogger (skill name, latency, output summary)
    6. Trả kết quả đã chuẩn hóa về cho Orchestrator
"""

import time
from typing import Any

from app.harness.logger import HarnessLogger
from app.harness.normalizer import SkillNormalizer
from app.harness.registry import SkillRegistry


class SkillRouter:
    """Nhận skill name + params, route đến đúng skill qua registry và log kết quả."""

    def __init__(
        self,
        registry: SkillRegistry,
        normalizer: SkillNormalizer | None = None,
        logger: HarnessLogger | None = None,
        max_retries: int = 1,
    ) -> None:
        self.registry = registry
        self.normalizer = normalizer or SkillNormalizer()
        self.logger = logger or HarnessLogger()
        self.max_retries = max(1, max_retries)

    def call(self, skill_name: str, **params: Any) -> dict[str, Any]:
        """Thực thi một skill theo tên, trả về output đã chuẩn hóa."""
        skill = self.registry.get(skill_name)
        normalized_input = self.normalizer.normalize_input(skill, params)
        lang = params.get("lang", "vi")

        start = time.perf_counter()
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                raw_output = skill.execute(**normalized_input)
                output = self.normalizer.normalize_output(skill, raw_output)
                latency_ms = (time.perf_counter() - start) * 1000
                self.logger.log_call(
                    skill_name=skill.name,
                    latency_ms=latency_ms,
                    output_summary=skill.summarize_output(output, lang=lang),
                    status="success",
                )
                return output
            except Exception as exc:
                last_error = exc

        latency_ms = (time.perf_counter() - start) * 1000
        error_prefix = "Error" if lang == "en" else "Lỗi"
        self.logger.log_call(
            skill_name=skill.name,
            latency_ms=latency_ms,
            output_summary=f"{error_prefix}: {last_error}",
            status="error",
            error=str(last_error),
        )
        raise last_error  # type: ignore[misc]
