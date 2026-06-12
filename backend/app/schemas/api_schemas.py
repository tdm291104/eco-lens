"""
Pydantic models cho API request/response.

- ScanRequest / ScanResponse: input ảnh (base64) và output kết quả scan
  + skill execution trace
- ChatRequest / ChatResponse: câu hỏi follow-up + scan_context và câu trả lời
- UserImpactResponse: tổng hợp tác động môi trường của user
- DisposalPoint / DisposalPointsResponse: điểm thu gom gần nhất
  (tên, địa chỉ, khoảng cách, giờ mở)
- SkillTraceStep: một bước trong skill execution trace
  (skill name, status, latency_ms, output_summary)

ScanRequest/ChatRequest có field `lang` ("vi" | "en", mặc định "vi" nếu
không truyền) để chọn ngôn ngữ cho nội dung do AI sinh ra và dữ liệu tĩnh
(local rules, category, badge/rank...).
"""

from pydantic import BaseModel


class SkillTraceStep(BaseModel):
    skill: str
    status: str
    latency_ms: float
    output_summary: str
    error: str | None = None


class ScanRequest(BaseModel):
    base64_image: str
    city: str | None = None
    user_id: str | None = None
    weight_g: float | None = None
    lang: str | None = None


class ScanResult(BaseModel):
    description: str
    objects: list[str]
    confidence: float
    category: str
    subcategory: str
    recyclable: bool
    is_hazardous: bool
    warning_level: str
    hazard_reason: str
    bin_color: str
    collection_day: str
    rules_notes: str
    steps: list[str]
    tips: list[str]
    warnings: list[str]
    co2_kg: float
    equivalent_km: float
    points: int
    badge: str
    streak: int


class ScanResponse(BaseModel):
    result: ScanResult
    trace: list[SkillTraceStep]


class ChatRequest(BaseModel):
    question: str
    scan_context: dict
    lang: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    trace: list[SkillTraceStep]


class UserImpactResponse(BaseModel):
    total_co2: float
    scans: int
    rank: str


class DisposalPoint(BaseModel):
    name: str
    city: str
    address: str
    lat: float
    lng: float
    waste_types: list[str]
    hours: str
    distance_km: float


class DisposalPointsResponse(BaseModel):
    points: list[DisposalPoint]
    distance: float
    hours: str
