/**
 * Translation strings cho UI tĩnh của EcoLens (EN/VI toggle).
 *
 * - `translations.en` / `translations.vi`: dict các chuỗi UI tĩnh.
 *   Giá trị có thể là string hoặc function (template) khi cần nội suy.
 * - `DEFAULT_LANG`: ngôn ngữ mặc định khi load app ("en" — submission
 *   hướng tới giám khảo quốc tế).
 * - Nội dung do AI sinh ra (description, disposal guide, chat...) và
 *   dữ liệu tĩnh từ backend (bin_color, category, badge/rank...) được
 *   dịch ở backend qua param `lang` gửi kèm request, không nằm ở đây.
 */

export const DEFAULT_LANG = 'en'

export const translations = {
  en: {
    // Upload screen
    uploadTitleLine1: 'Snap a photo, ',
    uploadTitleHighlight: 'know how to dispose of it instantly',
    uploadSubtitle:
      'Upload a photo of your waste — our multi-agent system identifies the material, checks local regulations, and guides you step by step.',
    removeImage: 'Remove image',
    dropHint: 'Drag and drop an image here',
    dropSubHint: 'or click to choose a file (PNG, JPG)',
    analyzeButton: 'Analyze image',

    // Processing screen
    pipelineError: 'Pipeline error',
    retry: 'Retry',
    back: 'Back',
    analyzing: 'Analyzing',
    skillsCompleted: (done, total, elapsed) => `${done}/${total} skills completed · ${elapsed}`,
    callingPipeline: 'Calling pipeline via Harness Layer (POST /api/scan)…',
    pipelineComplete: '✓ Pipeline complete — compiling results…',
    awaiting: 'awaiting…',

    // Result screen
    classificationResult: 'Classification result',
    scannedObject: 'Scanned object',
    recyclable: 'Recyclable',
    notRecyclable: 'Not recyclable',
    hazardWarning: 'Hazard warning',
    safeNotHazardous: 'Safe — not hazardous',
    disposalGuide: 'Disposal guide',
    co2Saved: 'CO₂ saved',
    co2SavedSub: (km) => `≈ ${km} km of motorbike travel`,
    greenPoints: 'Green points',
    streakWithBadge: (streak, badge) => `${streak}-day streak · ${badge}`,
    streakOnly: (streak) => `${streak}-day streak`,
    totalImpactPrefix: 'Your total impact: ',
    totalImpactMiddle: (scans) => ` · ${scans} scans · `,
    totalImpactSuffix: ' kg CO₂ saved',
    impactLoadError: (err) => `Couldn't load total impact (${err})`,
    impactLoading: 'Loading total impact…',
    nearestPoints: 'Nearest collection points',
    noPointsFound: (city) => `No matching collection points found near ${city}.`,
    pointsLoadError: (err) => `Couldn't load collection points (${err})`,
    pointsLoading: 'Finding collection points near you…',
    scanAnother: 'Scan another image',

    // Chat panel
    chatGreeting: (subcategory) =>
      `I've finished the analysis! Any more questions about how to dispose of ${subcategory || 'this item'}?`,
    askAdvisory: 'Ask the Advisory Agent',
    chatPlaceholder: 'E.g. Do I need to rinse the bottle before recycling?',
    chatError: (err) => `Error calling Advisory Agent: ${err}`,

    // API errors
    connectionError: 'Could not connect to the backend. Check that the server is running.',
    requestFailed: (path, status, detail) => `${path} failed (${status}): ${detail}`,
  },

  vi: {
    // Upload screen
    uploadTitleLine1: 'Chụp một bức ảnh, ',
    uploadTitleHighlight: 'biết ngay cách xử lý',
    uploadSubtitle:
      'Upload ảnh rác thải — hệ thống multi-agent sẽ nhận diện vật liệu, kiểm tra quy định địa phương và hướng dẫn xử lý từng bước.',
    removeImage: 'Xoá ảnh',
    dropHint: 'Kéo thả ảnh vào đây',
    dropSubHint: 'hoặc bấm để chọn ảnh từ thiết bị (PNG, JPG)',
    analyzeButton: 'Phân tích ảnh',

    // Processing screen
    pipelineError: 'Pipeline gặp lỗi',
    retry: 'Thử lại',
    back: 'Quay lại',
    analyzing: 'Đang phân tích',
    skillsCompleted: (done, total, elapsed) => `${done}/${total} skills hoàn thành · ${elapsed}`,
    callingPipeline: 'Đang gọi pipeline qua Harness Layer (POST /api/scan)…',
    pipelineComplete: '✓ Pipeline hoàn tất — đang tổng hợp kết quả…',
    awaiting: 'đang chờ…',

    // Result screen
    classificationResult: 'Kết quả phân loại',
    scannedObject: 'Vật thể đã quét',
    recyclable: 'Có thể tái chế',
    notRecyclable: 'Không thể tái chế',
    hazardWarning: 'Cảnh báo nguy hại',
    safeNotHazardous: 'An toàn — không nguy hại',
    disposalGuide: 'Hướng dẫn xử lý',
    co2Saved: 'CO₂ tiết kiệm',
    co2SavedSub: (km) => `≈ ${km} km đi xe máy`,
    greenPoints: 'Điểm xanh',
    streakWithBadge: (streak, badge) => `Chuỗi ${streak} ngày · ${badge}`,
    streakOnly: (streak) => `Chuỗi ${streak} ngày liên tiếp`,
    totalImpactPrefix: 'Tổng tác động của bạn: ',
    totalImpactMiddle: (scans) => ` · ${scans} lần quét · `,
    totalImpactSuffix: ' kg CO₂ đã tiết kiệm',
    impactLoadError: (err) => `Không tải được tổng tác động (${err})`,
    impactLoading: 'Đang tải tổng tác động…',
    nearestPoints: 'Điểm thu gom gần nhất',
    noPointsFound: (city) => `Không tìm thấy điểm thu gom phù hợp gần ${city}.`,
    pointsLoadError: (err) => `Không tải được điểm thu gom (${err})`,
    pointsLoading: 'Đang tìm điểm thu gom gần bạn…',
    scanAnother: 'Quét ảnh khác',

    // Chat panel
    chatGreeting: (subcategory) =>
      `Mình đã phân tích xong! Bạn có câu hỏi gì thêm về cách xử lý ${subcategory || 'vật thể này'} không?`,
    askAdvisory: 'Hỏi thêm Advisory Agent',
    chatPlaceholder: 'VD: Cần rửa chai trước khi tái chế không?',
    chatError: (err) => `Lỗi khi gọi Advisory Agent: ${err}`,

    // API errors
    connectionError: 'Không thể kết nối tới backend. Kiểm tra server đã chạy chưa.',
    requestFailed: (path, status, detail) => `${path} thất bại (${status}): ${detail}`,
  },
}

export function getTranslations(lang) {
  return translations[lang] || translations[DEFAULT_LANG]
}
