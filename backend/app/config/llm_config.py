"""
LLM configuration cho Groq API.

- Đọc GROQ_API_KEY từ environment variable (.env)
- Định nghĩa model mapping theo task_type:
    - "light"  -> meta-llama/llama-4-scout-17b-16e-instruct
                  (classify_waste_type, lookup_material_code, flag_hazardous,
                   suggest_alternatives, calculate_co2_saved, award_green_points, ...
                   - đây cũng là model vision duy nhất hiện có trên Groq, nên
                   call_vision_json dùng model "light" này cho analyze_image,
                   detect_material)
    - "heavy"  -> llama-3.3-70b-versatile
                  (generate_disposal_guide, answer_followup - text-only,
                   cần model mạnh hơn Scout. meta-llama/llama-4-maverick
                   hiện không khả dụng trên Groq nên dùng model này thay thế)
- get_groq_client(): trả về một Groq client instance duy nhất, reuse cho
  toàn bộ app (lazy init, raise lỗi rõ ràng nếu thiếu API key)
- get_model_for(task_type): trả về tên model tương ứng với task_type
"""

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

MODEL_MAP: dict[str, str] = {
    "light": "meta-llama/llama-4-scout-17b-16e-instruct",
    "heavy": "llama-3.3-70b-versatile",
}

_client: Groq | None = None


def get_groq_client() -> Groq:
    """Trả về Groq client instance duy nhất (khởi tạo lazy, reuse toàn app)."""
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY chưa được cấu hình. Copy backend/.env.example "
                "thành backend/.env và điền API key."
            )
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def get_model_for(task_type: str) -> str:
    """Trả về tên model Groq tương ứng với task_type ('light' hoặc 'heavy')."""
    try:
        return MODEL_MAP[task_type]
    except KeyError:
        raise ValueError(
            f"task_type '{task_type}' không hợp lệ. Chọn 'light' hoặc 'heavy'."
        ) from None
