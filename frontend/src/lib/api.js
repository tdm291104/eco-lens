/**
 * API client cho EcoLens backend (FastAPI Skill Harness).
 *
 * Gọi tới backend FastAPI - mặc định http://localhost:8000, có thể override
 * qua biến môi trường VITE_API_BASE_URL (xem .env.example).
 *
 * - scanImage(): POST /api/scan
 * - sendChatMessage(): POST /api/chat
 * - getUserImpact(): GET /api/user/{user_id}/impact
 * - getDisposalPoints(): GET /api/disposal-points
 *
 * Mỗi hàm nhận thêm `lang` ("en" | "vi") để: (1) gửi cho backend chọn
 * ngôn ngữ nội dung AI sinh ra + dữ liệu tĩnh, và (2) chọn ngôn ngữ cho
 * thông báo lỗi do chính client tạo ra (mất kết nối, request thất bại...).
 */

import { getTranslations } from './i18n'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path, options, lang) {
  const t = getTranslations(lang)
  let res
  try {
    res = await fetch(`${API_BASE_URL}${path}`, options)
  } catch {
    throw new Error(t.connectionError)
  }

  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail ? JSON.stringify(body.detail) : JSON.stringify(body)
    } catch {
      // giữ statusText nếu response không phải JSON
    }
    throw new Error(t.requestFailed(path, res.status, detail))
  }

  return res.json()
}

export function scanImage({ base64Image, city, userId, weightG, lang }) {
  const payload = { base64_image: base64Image }
  if (city) payload.city = city
  if (userId) payload.user_id = userId
  if (weightG != null) payload.weight_g = weightG
  if (lang) payload.lang = lang

  return request(
    '/api/scan',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
    lang,
  )
}

export function sendChatMessage({ question, scanContext, lang }) {
  return request(
    '/api/chat',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, scan_context: scanContext, lang }),
    },
    lang,
  )
}

export function getUserImpact(userId, lang) {
  const params = lang ? `?lang=${encodeURIComponent(lang)}` : ''
  return request(`/api/user/${encodeURIComponent(userId)}/impact${params}`, undefined, lang)
}

export function getDisposalPoints({ lat, lng, wasteType, lang }) {
  const params = new URLSearchParams({ lat, lng, waste_type: wasteType })
  if (lang) params.set('lang', lang)
  return request(`/api/disposal-points?${params.toString()}`, undefined, lang)
}
