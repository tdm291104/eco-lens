"""
Helper functions dùng chung cho các agent gọi Groq API và parse JSON response.

- call_text_json(prompt, task_type): gọi Groq (text-only) với model theo
  task_type ("light" -> Scout, "heavy" -> Llama 3.3 70B), parse JSON response.
- call_vision_json(base64_image, prompt): gọi Groq Scout (model "light" -
  model vision duy nhất hiện có trên Groq) với ảnh + prompt, parse JSON
  response.
- language_directive(lang): câu lệnh yêu cầu LLM trả lời bằng "vi" hoặc "en",
  dùng để chèn vào cuối prompt của các skill hỗ trợ song ngữ.

Cả 2 hàm gọi Groq yêu cầu model trả về JSON hợp lệ (response_format="json_object")
theo đúng cấu trúc được mô tả trong prompt của từng skill.
"""

import json
from typing import Any

from app.config.llm_config import get_groq_client, get_model_for


def call_text_json(prompt: str, task_type: str = "light", temperature: float = 0.2) -> dict[str, Any]:
    """Gọi Groq (text-only) với prompt, parse JSON response."""
    client = get_groq_client()
    model = get_model_for(task_type)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    return json.loads(response.choices[0].message.content)


def language_directive(lang: str) -> str:
    """Câu lệnh yêu cầu LLM trả lời các trường văn bản bằng tiếng Anh hoặc tiếng Việt."""
    if lang == "en":
        return "Write all text fields in English."
    return "Viết tất cả các trường văn bản bằng tiếng Việt."


def call_vision_json(base64_image: str, prompt: str, temperature: float = 0.2) -> dict[str, Any]:
    """Gọi Groq Scout (model vision duy nhất hiện có) với ảnh + prompt, parse JSON response."""
    client = get_groq_client()
    model = get_model_for("light")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    return json.loads(response.choices[0].message.content)
