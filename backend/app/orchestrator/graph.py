"""
LangGraph orchestrator.

Định nghĩa graph nối các skill theo đúng thứ tự pipeline scan:

    analyze_image
        -> classify_waste_type
        -> flag_hazardous
        -> get_local_rules
        -> generate_disposal_guide
        -> calculate_co2_saved
        -> award_green_points

Mỗi node gọi skill tương ứng qua SkillRouter (Harness Layer); output của
node trước được merge vào state và dùng làm input cho node sau.
Orchestrator không gọi trực tiếp vào agent - chỉ biết tên skill.

Lưu ý về input còn thiếu trong chuỗi 7 skill này:
- `classify_waste_type` cần field `material`. Pipeline không gọi riêng
  `detect_material`, nên tái dùng `description` (từ `analyze_image`) làm
  `material` - mô tả ảnh thường đã chứa thông tin chất liệu.
- `calculate_co2_saved` cần `weight_g`. Không skill nào trong chuỗi ước
  tính khối lượng, nên dùng `weight_g` từ initial_state nếu có, mặc định
  DEFAULT_WEIGHT_G (~50g, tương đương một chai nhựa nhỏ).
- `get_local_rules` cần `city`, lấy từ initial_state, mặc định DEFAULT_CITY.

Hỗ trợ song ngữ qua `lang` ("vi" | "en", mặc định DEFAULT_LANG) trong
initial_state - được truyền tới mọi skill liên quan đến văn bản hiển thị.
`get_local_rules` trả về `category_label` (category đã dịch theo `lang`) và
node này ghi đè field `category` trong state - các node sau (disposal guide,
award_green_points) dùng category đã dịch.
"""

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.harness.router import SkillRouter

DEFAULT_CITY = "TP. Hồ Chí Minh"
DEFAULT_WEIGHT_G = 50.0
DEFAULT_USER_ID = "demo"
DEFAULT_LANG = "vi"


class ScanState(TypedDict, total=False):
    # input
    base64_image: str
    city: str
    user_id: str
    weight_g: float
    lang: str

    # analyze_image
    description: str
    objects: list[str]
    confidence: float

    # classify_waste_type
    category: str
    subcategory: str
    recyclable: bool

    # flag_hazardous
    is_hazardous: bool
    warning_level: str
    hazard_reason: str

    # get_local_rules
    bin_color: str
    collection_day: str
    rules_notes: str

    # generate_disposal_guide
    steps: list[str]
    tips: list[str]
    warnings: list[str]

    # calculate_co2_saved
    co2_kg: float
    equivalent_km: float

    # award_green_points
    points: int
    badge: str
    streak: int


def build_scan_graph(router: SkillRouter):
    """Build LangGraph pipeline cho luồng scan ảnh, dùng skill từ `router`."""

    def analyze_image_node(state: ScanState) -> dict[str, Any]:
        result = router.call(
            "analyze_image",
            base64_image=state["base64_image"],
            lang=state.get("lang", DEFAULT_LANG),
        )
        return {
            "description": result["description"],
            "objects": result["objects"],
            "confidence": result["confidence"],
        }

    def classify_waste_type_node(state: ScanState) -> dict[str, Any]:
        result = router.call(
            "classify_waste_type",
            description=state["description"],
            material=state["description"],
            lang=state.get("lang", DEFAULT_LANG),
        )
        return {
            "category": result["category"],
            "subcategory": result["subcategory"],
            "recyclable": result["recyclable"],
        }

    def flag_hazardous_node(state: ScanState) -> dict[str, Any]:
        result = router.call(
            "flag_hazardous", category=state["category"], lang=state.get("lang", DEFAULT_LANG)
        )
        return {
            "is_hazardous": result["is_hazardous"],
            "warning_level": result["warning_level"],
            "hazard_reason": result["reason"],
        }

    def get_local_rules_node(state: ScanState) -> dict[str, Any]:
        result = router.call(
            "get_local_rules",
            city=state.get("city", DEFAULT_CITY),
            waste_category=state["category"],
            lang=state.get("lang", DEFAULT_LANG),
        )
        return {
            "bin_color": result["bin_color"],
            "collection_day": result["collection_day"],
            "rules_notes": result["notes"],
            "category": result["category_label"],
        }

    def generate_disposal_guide_node(state: ScanState) -> dict[str, Any]:
        result = router.call(
            "generate_disposal_guide",
            category=state["category"],
            location=state.get("city", DEFAULT_CITY),
            rules={
                "bin_color": state["bin_color"],
                "collection_day": state["collection_day"],
                "notes": state["rules_notes"],
            },
            lang=state.get("lang", DEFAULT_LANG),
        )
        return {
            "steps": result["steps"],
            "tips": result["tips"],
            "warnings": result["warnings"],
        }

    def calculate_co2_saved_node(state: ScanState) -> dict[str, Any]:
        result = router.call(
            "calculate_co2_saved",
            waste_type=state["subcategory"],
            weight_g=state.get("weight_g", DEFAULT_WEIGHT_G),
            lang=state.get("lang", DEFAULT_LANG),
        )
        return {"co2_kg": result["co2_kg"], "equivalent_km": result["equivalent_km"]}

    def award_green_points_node(state: ScanState) -> dict[str, Any]:
        result = router.call(
            "award_green_points",
            category=state["category"],
            is_hazardous=state["is_hazardous"],
            co2_kg=state.get("co2_kg", 0.0),
            user_id=state.get("user_id", DEFAULT_USER_ID),
            lang=state.get("lang", DEFAULT_LANG),
        )
        return {"points": result["points"], "badge": result["badge"], "streak": result["streak"]}

    graph = StateGraph(ScanState)
    graph.add_node("analyze_image", analyze_image_node)
    graph.add_node("classify_waste_type", classify_waste_type_node)
    graph.add_node("flag_hazardous", flag_hazardous_node)
    graph.add_node("get_local_rules", get_local_rules_node)
    graph.add_node("generate_disposal_guide", generate_disposal_guide_node)
    graph.add_node("calculate_co2_saved", calculate_co2_saved_node)
    graph.add_node("award_green_points", award_green_points_node)

    graph.set_entry_point("analyze_image")
    graph.add_edge("analyze_image", "classify_waste_type")
    graph.add_edge("classify_waste_type", "flag_hazardous")
    graph.add_edge("flag_hazardous", "get_local_rules")
    graph.add_edge("get_local_rules", "generate_disposal_guide")
    graph.add_edge("generate_disposal_guide", "calculate_co2_saved")
    graph.add_edge("calculate_co2_saved", "award_green_points")
    graph.add_edge("award_green_points", END)

    return graph.compile()


def run_scan_pipeline(router: SkillRouter, **initial_state: Any) -> ScanState:
    """Chạy pipeline scan đầy đủ qua LangGraph, trả về state cuối (kết quả tổng hợp)."""
    graph = build_scan_graph(router)
    return graph.invoke(initial_state)  # type: ignore[arg-type]
