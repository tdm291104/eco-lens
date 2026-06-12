"""
Scoring Agent (công thức thuần + SQLite).

Skills:
- calculate_co2_saved(waste_type, weight_g) -> {co2_kg, equivalent_km}
    Công thức thuần - ước tính lượng CO2 tiết kiệm theo loại rác và khối lượng.
- award_green_points(category, is_hazardous, co2_kg?, user_id?) -> {points, badge, streak}
    Công thức thuần để tính điểm; đọc/ghi streak + tổng điểm/CO2 của user vào SQLite
    (user_id mặc định "demo" nếu không truyền - phù hợp bản demo single-user).
- get_user_impact(user_id) -> {total_co2, scans, rank}
    Query SQLite - tổng hợp tác động môi trường tích lũy của user.
"""

from datetime import date, timedelta
from typing import Any

from app.db.database import get_session
from app.db.models import UserImpact
from app.harness.registry import SkillRegistry
from app.harness.skill import Skill


class CalculateCo2SavedSkill(Skill):
    """Ước tính kg CO2 tiết kiệm được khi xử lý/tái chế đúng cách."""

    name = "calculate_co2_saved"
    description = "Ước tính CO2 tiết kiệm theo loại rác và khối lượng (công thức thuần)"
    input_schema = {"waste_type": "str", "weight_g": "float"}
    output_schema = {"co2_kg": "float", "equivalent_km": "float"}

    # kg CO2 tiết kiệm cho mỗi kg rác được xử lý/tái chế đúng cách, theo loại vật liệu
    # (gồm cả từ khóa tiếng Việt và tiếng Anh để khớp với subcategory ở cả 2 ngôn ngữ)
    CO2_FACTOR_PER_KG: dict[str, float] = {
        "pet": 1.65,
        "nhựa": 1.5,
        "plastic": 1.5,
        "giấy": 0.9,
        "paper": 0.9,
        "thủy tinh": 0.3,
        "glass": 0.3,
        "kim loại": 2.0,
        "metal": 2.0,
        "hữu cơ": 0.2,
        "organic": 0.2,
    }
    DEFAULT_FACTOR_PER_KG = 1.0

    # 1 km di chuyển bằng xe máy ước tính phát ra ~0.205 kg CO2
    CO2_KG_PER_KM = 0.205

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        waste_type = kwargs["waste_type"]
        weight_g = kwargs["weight_g"]

        factor = self.DEFAULT_FACTOR_PER_KG
        waste_type_lower = waste_type.lower()
        for keyword, kg_factor in self.CO2_FACTOR_PER_KG.items():
            if keyword in waste_type_lower:
                factor = kg_factor
                break

        co2_kg = round((weight_g / 1000.0) * factor, 3)
        equivalent_km = round(co2_kg / self.CO2_KG_PER_KM, 2)
        return {"co2_kg": co2_kg, "equivalent_km": equivalent_km}

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        if lang == "en":
            return (
                f"Saved {output['co2_kg']} kg CO₂ ≈ "
                f"{output['equivalent_km']} km of motorbike travel"
            )
        return (
            f"Tiết kiệm {output['co2_kg']} kg CO₂ ≈ "
            f"{output['equivalent_km']} km di chuyển bằng xe máy"
        )


class AwardGreenPointsSkill(Skill):
    """Tính điểm xanh cho lần scan và cập nhật streak/tổng điểm/CO2 của user trong SQLite."""

    name = "award_green_points"
    description = "Tính điểm xanh + streak cho người dùng (công thức thuần + SQLite)"
    input_schema = {
        "category": "str",
        "is_hazardous": "bool",
        "co2_kg": "float",
        "user_id": "str",
    }
    output_schema = {"points": "int", "badge": "str", "streak": "int"}

    BASE_POINTS = 10
    RECYCLABLE_BONUS = 5
    HAZARDOUS_HANDLING_BONUS = 10
    RECYCLABLE_KEYWORDS = ("tái chế", "recycl")

    BADGE_THRESHOLDS: list[tuple[int, str]] = [
        (100, "Eco Champion"),
        (50, "Eco Warrior"),
        (20, "Eco Starter"),
    ]

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        category = kwargs["category"]
        is_hazardous = kwargs["is_hazardous"]
        co2_kg = kwargs.get("co2_kg", 0.0)
        user_id = kwargs.get("user_id") or "demo"

        points = self.BASE_POINTS
        if any(keyword in category.lower() for keyword in self.RECYCLABLE_KEYWORDS):
            points += self.RECYCLABLE_BONUS
        if is_hazardous:
            points += self.HAZARDOUS_HANDLING_BONUS

        streak, total_points = _record_scan(user_id, points, co2_kg)

        badge = ""
        for threshold, badge_name in self.BADGE_THRESHOLDS:
            if total_points >= threshold:
                badge = badge_name
                break

        return {"points": points, "badge": badge, "streak": streak}

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        if lang == "en":
            badge_suffix = f" — badge {output['badge']}" if output.get("badge") else ""
            return f"+{output['points']} green points — {output['streak']}-day streak{badge_suffix}"
        badge_suffix = f" — huy hiệu {output['badge']}" if output.get("badge") else ""
        return f"+{output['points']} điểm xanh — chuỗi quét {output['streak']} ngày liên tiếp{badge_suffix}"


class GetUserImpactSkill(Skill):
    """Tổng hợp tác động môi trường tích lũy của một user, đọc từ SQLite."""

    name = "get_user_impact"
    description = "Tổng hợp tác động môi trường tích lũy của user (SQLite)"
    input_schema = {"user_id": "str", "lang": "str"}
    output_schema = {"total_co2": "float", "scans": "int", "rank": "str"}

    RANK_THRESHOLDS: list[tuple[int, str]] = [
        (200, "Eco Champion"),
        (100, "Eco Warrior"),
        (30, "Eco Starter"),
    ]
    DEFAULT_RANK_VI = "Người mới"
    DEFAULT_RANK_EN = "Newcomer"

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        user_id = kwargs["user_id"]
        lang = kwargs.get("lang", "vi")
        default_rank = self.DEFAULT_RANK_EN if lang == "en" else self.DEFAULT_RANK_VI

        session = get_session()
        try:
            record = session.get(UserImpact, user_id)
        finally:
            session.close()

        if record is None:
            return {"total_co2": 0.0, "scans": 0, "rank": default_rank}

        rank = default_rank
        for threshold, rank_name in self.RANK_THRESHOLDS:
            if record.total_points >= threshold:
                rank = rank_name
                break

        return {"total_co2": record.total_co2_kg, "scans": record.scan_count, "rank": rank}

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        if lang == "en":
            return f"{output['scans']} scans, {output['total_co2']} kg CO₂, rank {output['rank']}"
        return f"{output['scans']} lượt scan, {output['total_co2']} kg CO₂, hạng {output['rank']}"


def _record_scan(user_id: str, points: int, co2_kg: float) -> tuple[int, int]:
    """
    Cập nhật UserImpact sau một lần scan: cộng điểm/CO2, tính lại streak theo ngày.

    Trả về (streak, total_points) sau khi cập nhật.
    """
    today = date.today()
    yesterday_iso = (today - timedelta(days=1)).isoformat()
    today_iso = today.isoformat()

    session = get_session()
    try:
        record = session.get(UserImpact, user_id)
        if record is None:
            record = UserImpact(
                user_id=user_id,
                total_co2_kg=0.0,
                total_points=0,
                scan_count=0,
                streak=0,
                last_scan_date=None,
            )
            session.add(record)

        if record.last_scan_date == today_iso:
            pass  # đã scan hôm nay, streak giữ nguyên
        elif record.last_scan_date == yesterday_iso:
            record.streak += 1
        else:
            record.streak = 1

        record.total_co2_kg = round(record.total_co2_kg + co2_kg, 3)
        record.total_points += points
        record.scan_count += 1
        record.last_scan_date = today_iso

        session.commit()
        return record.streak, record.total_points
    finally:
        session.close()


def register(registry: SkillRegistry) -> None:
    """Đăng ký toàn bộ skill của Scoring Agent vào registry."""
    registry.register(CalculateCo2SavedSkill())
    registry.register(AwardGreenPointsSkill())
    registry.register(GetUserImpactSkill())
