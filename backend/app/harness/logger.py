"""
HarnessLogger - ghi log thực thi skill để build Skill Execution Trace.

Mỗi lần SkillRouter gọi một skill, logger ghi lại:
- skill name
- latency (ms)
- tóm tắt output (output summary, ngắn gọn để hiển thị trên UI)
- trạng thái (success / error) và lỗi (nếu có)

get_trace(): trả về danh sách các bước đã log theo thứ tự thực thi,
dùng làm response "skill execution trace" cho POST /api/scan.
"""

from dataclasses import dataclass


@dataclass
class SkillLogEntry:
    skill_name: str
    status: str
    latency_ms: float
    output_summary: str
    error: str | None = None


class HarnessLogger:
    """Ghi log từng lần skill được gọi, dùng để build Skill Execution Trace."""

    def __init__(self) -> None:
        self._entries: list[SkillLogEntry] = []

    def log_call(
        self,
        skill_name: str,
        latency_ms: float,
        output_summary: str,
        status: str = "success",
        error: str | None = None,
    ) -> SkillLogEntry:
        entry = SkillLogEntry(
            skill_name=skill_name,
            status=status,
            latency_ms=round(latency_ms, 2),
            output_summary=output_summary,
            error=error,
        )
        self._entries.append(entry)
        return entry

    def get_trace(self) -> list[dict[str, object]]:
        """Trả về skill execution trace theo thứ tự thực thi."""
        trace = []
        for entry in self._entries:
            step: dict[str, object] = {
                "skill": entry.skill_name,
                "status": entry.status,
                "latency_ms": entry.latency_ms,
                "output_summary": entry.output_summary,
            }
            if entry.error:
                step["error"] = entry.error
            trace.append(step)
        return trace

    def reset(self) -> None:
        """Xóa toàn bộ log - gọi trước mỗi lần chạy pipeline scan mới."""
        self._entries.clear()
