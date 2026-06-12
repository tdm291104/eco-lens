"""
Localization Agent (mock data JSON - app/data/local_rules.json).

Skills:
- get_local_rules(city, waste_category) -> {bin_color, collection_day, notes}
    Tra cứu quy định phân loại rác theo tỉnh/thành từ mock data.
- find_disposal_points(lat, lng, waste_type) -> {points[], distance, hours}
    Tìm điểm thu gom gần nhất (mock data, sắp xếp theo khoảng cách haversine).
- get_collection_schedule(district, waste_type) -> {schedule[], next_pickup}
    Lấy lịch xe rác theo khu vực (mock data).

Toàn bộ logic là thuần Python, không gọi LLM. Mock data được load một lần
và cache trong dict in-memory.
"""

import json
import math
from pathlib import Path
from typing import Any

from app.harness.registry import SkillRegistry
from app.harness.skill import Skill

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "local_rules.json"
_data_cache: dict[str, Any] | None = None

# Nhãn hiển thị song ngữ cho 4 nhóm rác chính (key = mã nội bộ tiếng Việt,
# dùng để tra local_rules.json và disposal_points.waste_types).
CATEGORY_LABELS: dict[str, dict[str, str]] = {
    "Rác tái chế": {"vi": "Rác tái chế", "en": "Recyclable waste"},
    "Rác hữu cơ": {"vi": "Rác hữu cơ", "en": "Organic waste"},
    "Rác nguy hại": {"vi": "Rác nguy hại", "en": "Hazardous waste"},
    "Rác thông thường": {"vi": "Rác thông thường", "en": "General waste"},
}


def translate_category(category: str, lang: str) -> str:
    """Dịch mã nhóm rác nội bộ (tiếng Việt) sang nhãn hiển thị theo `lang`."""
    return CATEGORY_LABELS.get(category, {}).get(lang, category)


def canonical_category(label: str) -> str:
    """Quy đổi một nhãn nhóm rác (vi hoặc en) về mã nội bộ tiếng Việt."""
    for key, labels in CATEGORY_LABELS.items():
        if label in labels.values():
            return key
    return label


def _load_data() -> dict[str, Any]:
    """Load mock localization data từ JSON, cache trong dict in-memory."""
    global _data_cache
    if _data_cache is None:
        with open(_DATA_PATH, encoding="utf-8") as f:
            _data_cache = json.load(f)
    return _data_cache


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Khoảng cách (km) giữa 2 điểm tọa độ theo công thức haversine."""
    radius_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius_km * math.asin(math.sqrt(a))


class GetLocalRulesSkill(Skill):
    """Tra quy định phân loại rác (thùng màu gì, ngày thu gom, lưu ý) theo tỉnh/thành."""

    name = "get_local_rules"
    description = "Tra quy định phân loại rác theo tỉnh/thành (mock data)"
    input_schema = {"city": "str", "waste_category": "str", "lang": "str"}
    output_schema = {"bin_color": "str", "collection_day": "str", "notes": "str", "category_label": "str"}

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        data = _load_data()
        lang = kwargs.get("lang", "vi")
        city_rules = data["rules_by_city"].get(kwargs["city"], {})
        rule = city_rules.get(kwargs["waste_category"], data["default_rule"])

        if lang == "en":
            return {
                "bin_color": rule.get("bin_color_en", rule["bin_color"]),
                "collection_day": rule.get("collection_day_en", rule["collection_day"]),
                "notes": rule.get("notes_en", rule["notes"]),
                "category_label": translate_category(kwargs["waste_category"], "en"),
            }
        return {
            "bin_color": rule["bin_color"],
            "collection_day": rule["collection_day"],
            "notes": rule["notes"],
            "category_label": kwargs["waste_category"],
        }

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        sep = " — " if lang != "en" else " - "
        return f"{output.get('bin_color', '')}{sep}{output.get('collection_day', '')}"


class FindDisposalPointsSkill(Skill):
    """Tìm điểm thu gom gần nhất theo loại rác, sắp xếp theo khoảng cách."""

    name = "find_disposal_points"
    description = "Tìm điểm thu gom gần nhất theo loại rác (mock data)"
    input_schema = {"lat": "float", "lng": "float", "waste_type": "str", "lang": "str"}
    output_schema = {"points": "list", "distance": "float", "hours": "str"}

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        data = _load_data()
        lat, lng = kwargs["lat"], kwargs["lng"]
        lang = kwargs.get("lang", "vi")
        waste_type_key = canonical_category(kwargs["waste_type"])

        candidates = [p for p in data["disposal_points"] if waste_type_key in p["waste_types"]]
        if not candidates:
            candidates = data["disposal_points"]

        points = []
        for point in candidates:
            distance_km = round(_haversine_km(lat, lng, point["lat"], point["lng"]), 2)
            entry = {**point, "distance_km": distance_km}
            if lang == "en":
                entry["waste_types"] = [translate_category(w, "en") for w in point["waste_types"]]
            points.append(entry)
        points.sort(key=lambda p: p["distance_km"])

        nearest = points[0] if points else None
        return {
            "points": points,
            "distance": nearest["distance_km"] if nearest else 0.0,
            "hours": nearest["hours"] if nearest else "",
        }

    def summarize_output(self, output: dict[str, Any], lang: str = "vi") -> str:
        if lang == "en":
            return f"Found {len(output['points'])} collection points, nearest {output['distance']} km away"
        return f"Tìm thấy {len(output['points'])} điểm thu gom, gần nhất {output['distance']} km"


class GetCollectionScheduleSkill(Skill):
    """Lấy lịch thu gom rác theo khu vực (quận/huyện) và loại rác."""

    name = "get_collection_schedule"
    description = "Lấy lịch xe rác theo khu vực (mock data)"
    input_schema = {"district": "str", "waste_type": "str"}
    output_schema = {"schedule": "list", "next_pickup": "str"}

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        data = _load_data()
        district_schedules = data["collection_schedules"].get(kwargs["district"], {})
        entry = district_schedules.get(kwargs["waste_type"], data["default_schedule"])
        return dict(entry)

    def summarize_output(self, output: dict[str, Any]) -> str:
        return f"{', '.join(output.get('schedule', []))} — kế tiếp: {output.get('next_pickup', '')}"


def register(registry: SkillRegistry) -> None:
    """Đăng ký toàn bộ skill của Localization Agent vào registry."""
    registry.register(GetLocalRulesSkill())
    registry.register(FindDisposalPointsSkill())
    registry.register(GetCollectionScheduleSkill())
