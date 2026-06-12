import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  UploadCloud,
  ImageOff,
  Sparkles,
  Loader2,
  CheckCircle2,
  Circle,
  XCircle,
  AlertOctagon,
  Recycle,
  AlertTriangle,
  Leaf,
  MapPin,
  Send,
  Award,
  RotateCcw,
  Eye,
  Tags,
  ShieldAlert,
  MapPinned,
  ListChecks,
  Gauge,
  Trophy,
  Bot,
  User,
} from 'lucide-react'
import { scanImage, sendChatMessage, getUserImpact, getDisposalPoints } from './lib/api'
import { DEFAULT_LANG, getTranslations } from './lib/i18n'

// ---------------------------------------------------------------------------
// Constants — pipeline metadata (icon/agent mapping cho Skill Execution Trace)
// ---------------------------------------------------------------------------

const DEFAULT_CITY = 'TP. Hồ Chí Minh'
const DEFAULT_USER_ID = 'demo'
// Toạ độ trung tâm TP. Hồ Chí Minh — dùng khi không lấy được vị trí trình duyệt
const DEFAULT_COORDS = { lat: 10.7769, lng: 106.7009 }

const SKILL_ORDER = [
  'analyze_image',
  'classify_waste_type',
  'flag_hazardous',
  'get_local_rules',
  'generate_disposal_guide',
  'calculate_co2_saved',
  'award_green_points',
]

const SKILL_META = {
  analyze_image: { agent: 'Vision Agent', icon: Eye },
  classify_waste_type: { agent: 'Classification Agent', icon: Tags },
  flag_hazardous: { agent: 'Classification Agent', icon: ShieldAlert },
  get_local_rules: { agent: 'Localization Agent', icon: MapPinned },
  generate_disposal_guide: { agent: 'Advisory Agent', icon: ListChecks },
  calculate_co2_saved: { agent: 'Scoring Agent', icon: Gauge },
  award_green_points: { agent: 'Scoring Agent', icon: Trophy },
}

const BIN_COLOR_SWATCHES = [
  { match: /vàng|yellow/i, color: '#facc15' },
  { match: /xanh lá|green/i, color: '#34d399' },
  { match: /xanh dương|xanh da trời|blue/i, color: '#60a5fa' },
  { match: /đỏ|red/i, color: '#f87171' },
  { match: /cam|orange/i, color: '#fb923c' },
  { match: /xám|gray|grey/i, color: '#9ca3af' },
  { match: /đen|black/i, color: '#3f3f46' },
  { match: /trắng|white/i, color: '#e5e7eb' },
]

function binColorSwatch(text) {
  const found = BIN_COLOR_SWATCHES.find((c) => c.match.test(text || ''))
  return found ? found.color : '#9ca3af'
}

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------

function useTypewriter(text, active, speed = 14) {
  const [output, setOutput] = useState('')
  const [trackedText, setTrackedText] = useState(text)

  if (active && text && text !== trackedText) {
    setTrackedText(text)
    setOutput('')
  }

  useEffect(() => {
    if (!active || !text) return
    let i = 0
    const interval = setInterval(() => {
      i += 1
      setOutput(text.slice(0, i))
      if (i >= text.length) clearInterval(interval)
    }, speed)
    return () => clearInterval(interval)
  }, [text, active, speed])

  return output
}

function formatElapsed(ms) {
  return `${(ms / 1000).toFixed(2)}s`
}

export default function EcoLensDemo() {
  const [screen, setScreen] = useState('upload') // upload | processing | result
  const [image, setImage] = useState(null)
  const [fileName, setFileName] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [scan, setScan] = useState({ status: 'idle' })
  const [attempt, setAttempt] = useState(0)
  const [lang, setLang] = useState(DEFAULT_LANG)
  const t = getTranslations(lang)

  const runScan = useCallback(() => {
    if (!image) return
    setAttempt((a) => a + 1)
    setScan({ status: 'loading' })
    const base64 = image.includes(',') ? image.split(',')[1] : image
    scanImage({ base64Image: base64, city: DEFAULT_CITY, userId: DEFAULT_USER_ID, lang })
      .then((data) => setScan({ status: 'success', result: data.result, trace: data.trace }))
      .catch((err) => setScan({ status: 'error', error: err.message }))
  }, [image, lang])

  return (
    <div className="bg-grain min-h-screen relative overflow-x-hidden">
      <BackgroundGlow />
      <div className="relative z-10 max-w-3xl mx-auto px-4 py-10 sm:py-14">
        <Header lang={lang} setLang={setLang} />
        <AnimatePresence mode="wait">
          {screen === 'upload' && (
            <UploadScreen
              key="upload"
              t={t}
              image={image}
              setImage={setImage}
              fileName={fileName}
              setFileName={setFileName}
              dragActive={dragActive}
              setDragActive={setDragActive}
              onAnalyze={() => {
                setScreen('processing')
                runScan()
              }}
            />
          )}
          {screen === 'processing' && (
            <ProcessingScreen
              key="processing"
              t={t}
              image={image}
              scan={scan}
              attempt={attempt}
              onDone={() => setScreen('result')}
              onRetry={runScan}
              onBack={() => {
                setScreen('upload')
                setScan({ status: 'idle' })
              }}
            />
          )}
          {screen === 'result' && (
            <ResultScreen
              key="result"
              t={t}
              lang={lang}
              image={image}
              result={scan.result}
              city={DEFAULT_CITY}
              onReset={() => {
                setScreen('upload')
                setImage(null)
                setFileName('')
                setScan({ status: 'idle' })
              }}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

function BackgroundGlow() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0">
      <div
        className="absolute -top-40 -left-32 h-96 w-96 rounded-full blur-3xl opacity-25"
        style={{ background: 'radial-gradient(circle, rgba(182,255,77,0.5), transparent 70%)' }}
      />
      <div
        className="absolute bottom-0 right-0 h-[28rem] w-[28rem] rounded-full blur-3xl opacity-20"
        style={{ background: 'radial-gradient(circle, rgba(52,211,153,0.45), transparent 70%)' }}
      />
    </div>
  )
}

function Header({ lang, setLang }) {
  return (
    <header className="flex items-center justify-between mb-10">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-ink-800 border border-ink-600 flex items-center justify-center shadow-[0_0_20px_rgba(182,255,77,0.15)]">
          <Leaf className="h-5 w-5 text-lime" strokeWidth={2.25} />
        </div>
        <div>
          <h1 className="font-display text-2xl tracking-tight text-paper leading-none">
            Eco<span className="text-lime text-glow">Lens</span>
          </h1>
          <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-mist mt-1">
            Skill Harness Console
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="hidden sm:flex items-center gap-2 font-mono text-[11px] text-mist border border-ink-700 rounded-full px-3 py-1.5 bg-ink-900/60">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald animate-pulse" />
          5 agents · 15 skills online
        </div>
        <div className="flex items-center rounded-full border border-ink-700 bg-ink-900/60 p-0.5 font-mono text-[11px] uppercase tracking-wider">
          {['en', 'vi'].map((code) => (
            <button
              key={code}
              type="button"
              onClick={() => setLang(code)}
              aria-pressed={lang === code}
              className={`rounded-full px-2.5 py-1 transition-colors ${
                lang === code ? 'bg-lime text-ink-950' : 'text-mist hover:text-paper'
              }`}
            >
              {code}
            </button>
          ))}
        </div>
      </div>
    </header>
  )
}

// ---------------------------------------------------------------------------
// Screen 2 — Processing / Skill Execution Trace
// ---------------------------------------------------------------------------

const EMPTY_TRACE = []

function ProcessingScreen({ t, image, scan, attempt, onDone, onRetry, onBack }) {
  if (scan.status === 'error') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -12 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
      >
        <div className="rounded-2xl border border-hazard/30 bg-hazard/5 p-6 sm:p-8 text-center">
          <AlertOctagon className="h-10 w-10 text-hazard mx-auto mb-4" />
          <h2 className="font-display text-2xl text-paper mb-2">{t.pipelineError}</h2>
          <p className="font-mono text-xs text-mist/80 mb-6 break-all">{scan.error}</p>
          <div className="flex justify-center gap-3">
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center gap-2 rounded-full bg-lime text-ink-950 px-5 py-2.5 text-sm font-semibold hover:shadow-[0_0_30px_rgba(182,255,77,0.4)] transition-shadow"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              {t.retry}
            </button>
            <button
              type="button"
              onClick={onBack}
              className="inline-flex items-center gap-2 rounded-full border border-ink-700 px-5 py-2.5 text-sm text-mist hover:text-paper hover:border-ink-500 transition-colors"
            >
              {t.back}
            </button>
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
    >
      <ProcessingBody key={attempt} t={t} image={image} scan={scan} onDone={onDone} />
    </motion.div>
  )
}

function ProcessingBody({ t, image, scan, onDone }) {
  const [revealCount, setRevealCount] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const startRef = useRef(null)

  useEffect(() => {
    startRef.current = performance.now()
    const tick = setInterval(() => {
      setElapsed(performance.now() - startRef.current)
    }, 40)
    return () => clearInterval(tick)
  }, [])

  const trace = scan.trace ?? EMPTY_TRACE

  useEffect(() => {
    if (scan.status !== 'success') return
    if (revealCount >= trace.length) {
      const t = setTimeout(onDone, 900)
      return () => clearTimeout(t)
    }
    const step = trace[revealCount]
    const delay = Math.min(Math.max(step.latency_ms, 350), 1400)
    const t = setTimeout(() => setRevealCount((c) => c + 1), delay)
    return () => clearTimeout(t)
  }, [scan.status, revealCount, trace, onDone])

  const total = trace.length || SKILL_ORDER.length
  const doneCount = scan.status === 'success' ? Math.min(revealCount, trace.length) : 0
  const progressPct = (doneCount / total) * 100
  const allDone = scan.status === 'success' && revealCount >= trace.length

  return (
    <>
      <div className="flex items-center gap-4 mb-6">
        {image && (
          <img
            src={image}
            alt={t.analyzing}
            className="h-14 w-14 rounded-lg object-cover border border-ink-600 flex-shrink-0"
          />
        )}
        <div className="flex-1 min-w-0">
          <h2 className="font-display text-2xl text-paper flex items-center gap-2">
            {t.analyzing}
            <span className="inline-flex gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-lime animate-bounce [animation-delay:-0.3s]" />
              <span className="h-1.5 w-1.5 rounded-full bg-lime animate-bounce [animation-delay:-0.15s]" />
              <span className="h-1.5 w-1.5 rounded-full bg-lime animate-bounce" />
            </span>
          </h2>
          <p className="font-mono text-xs text-mist mt-1">
            {t.skillsCompleted(doneCount, total, formatElapsed(elapsed))}
          </p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 w-full rounded-full bg-ink-800 overflow-hidden mb-6 border border-ink-700">
        <motion.div
          className="h-full rounded-full bg-gradient-to-r from-emerald to-lime"
          animate={{ width: `${progressPct}%` }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          style={{ boxShadow: '0 0 12px rgba(182,255,77,0.6)' }}
        />
      </div>

      {/* Skill trace */}
      <div className="rounded-2xl border border-ink-700 bg-ink-900/60 scanlines overflow-hidden">
        <div className="flex items-center justify-between px-4 sm:px-5 py-3 border-b border-ink-700 bg-ink-800/50">
          <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-mist">
            Skill Execution Trace
          </span>
          <span className="font-mono text-[11px] text-mist/70">harness.run()</span>
        </div>
        <div>
          {scan.status === 'loading' ? (
            <SkillRow
              t={t}
              id={SKILL_ORDER[0]}
              agent={SKILL_META[SKILL_ORDER[0]].agent}
              Icon={SKILL_META[SKILL_ORDER[0]].icon}
              status="running"
              summary={t.callingPipeline}
              latencyMs={null}
              visible
              isLast
            />
          ) : (
            trace.map((step, i) => {
              const meta = SKILL_META[step.skill] ?? { agent: 'Agent', icon: Bot }
              const rowStatus =
                i < revealCount ? (step.status === 'error' ? 'error' : 'done') : i === revealCount ? 'running' : 'pending'
              return (
                <SkillRow
                  key={`${step.skill}-${i}`}
                  t={t}
                  id={step.skill}
                  agent={meta.agent}
                  Icon={meta.icon}
                  status={rowStatus}
                  summary={step.status === 'error' ? step.error || step.output_summary : step.output_summary}
                  latencyMs={step.latency_ms}
                  visible={i <= revealCount}
                  isLast={i === trace.length - 1}
                />
              )
            })
          )}
        </div>
      </div>

      {allDone && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center font-mono text-xs text-emerald mt-4"
        >
          {t.pipelineComplete}
        </motion.p>
      )}
    </>
  )
}

function SkillRow({ t, id, agent, Icon, status, summary, latencyMs, visible, isLast }) {
  const typed = useTypewriter(summary, status !== 'pending' && visible, 12)

  if (!visible) return null

  return (
    <motion.div
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className={`relative flex items-start gap-3 px-4 sm:px-5 py-3.5 transition-colors duration-300
        ${!isLast ? 'border-b border-ink-700/60' : ''}
        ${status === 'running' ? 'bg-lime/[0.04]' : ''}
        ${status === 'error' ? 'bg-hazard/[0.04]' : ''}
      `}
    >
      {/* active left accent bar */}
      {status === 'running' && (
        <motion.span
          layoutId="active-skill-bar"
          className="absolute left-0 top-0 bottom-0 w-0.5 bg-lime"
          style={{ boxShadow: '0 0 8px rgba(182,255,77,0.8)' }}
        />
      )}
      {status === 'error' && (
        <span
          className="absolute left-0 top-0 bottom-0 w-0.5 bg-hazard"
          style={{ boxShadow: '0 0 8px rgba(248,113,113,0.8)' }}
        />
      )}

      {/* status icon */}
      <div className="mt-0.5 flex-shrink-0">
        {status === 'pending' && <Circle className="h-4 w-4 text-ink-600" />}
        {status === 'running' && <Loader2 className="h-4 w-4 text-lime animate-spin" />}
        {status === 'done' && <CheckCircle2 className="h-4 w-4 text-emerald" />}
        {status === 'error' && <XCircle className="h-4 w-4 text-hazard" />}
      </div>

      {/* skill icon */}
      <div
        className={`mt-0.5 flex-shrink-0 h-6 w-6 rounded-md flex items-center justify-center border transition-colors duration-300
          ${status === 'pending'
            ? 'border-ink-700 text-ink-600'
            : status === 'error'
              ? 'border-hazard/30 text-hazard bg-hazard/5'
              : 'border-lime/30 text-lime bg-lime/5'}`}
      >
        <Icon className="h-3.5 w-3.5" />
      </div>

      {/* name + summary */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-mono text-sm text-paper">{id}</span>
          <span className="font-mono text-[10px] uppercase tracking-wider text-mist/60 border border-ink-700 rounded px-1.5 py-0.5">
            {agent}
          </span>
        </div>
        <p className="font-mono text-xs text-mist mt-1.5 min-h-[1.25rem] leading-relaxed">
          {status === 'pending' ? (
            <span className="text-ink-600">{t.awaiting}</span>
          ) : (
            <>
              {typed}
              {typed.length < (summary?.length ?? 0) && <span className="caret">▋</span>}
            </>
          )}
        </p>
      </div>

      {/* duration */}
      <div className="flex-shrink-0 font-mono text-xs tabular-nums">
        {status === 'done' ? (
          <span className="text-emerald">{latencyMs}ms</span>
        ) : status === 'error' ? (
          <span className="text-hazard">{latencyMs}ms</span>
        ) : status === 'running' ? (
          <span className="text-lime/70 animate-pulse">…</span>
        ) : (
          <span className="text-ink-600">—</span>
        )}
      </div>
    </motion.div>
  )
}

// ---------------------------------------------------------------------------
// Screen 1 — Upload
// ---------------------------------------------------------------------------

function UploadScreen({ t, image, setImage, fileName, setFileName, dragActive, setDragActive, onAnalyze }) {
  const inputRef = useRef(null)

  const handleFile = useCallback((file) => {
    if (!file || !file.type.startsWith('image/')) return
    setFileName(file.name)
    const reader = new FileReader()
    reader.onload = (e) => setImage(e.target.result)
    reader.readAsDataURL(file)
  }, [setFileName, setImage])

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
    >
      <div className="text-center mb-8">
        <h2 className="font-display text-3xl sm:text-4xl text-paper mb-3">
          {t.uploadTitleLine1}
          <span className="text-lime text-glow">{t.uploadTitleHighlight}</span>
        </h2>
        <p className="text-mist max-w-lg mx-auto leading-relaxed">{t.uploadSubtitle}</p>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragActive(true)
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragActive(false)
          handleFile(e.dataTransfer.files?.[0])
        }}
        onClick={() => inputRef.current?.click()}
        className={`group relative cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-300 p-10 sm:p-14 flex flex-col items-center justify-center text-center
          ${dragActive
            ? 'border-lime bg-lime/5 scale-[1.01] shadow-[0_0_40px_rgba(182,255,77,0.2)]'
            : 'border-ink-600 bg-ink-900/50 hover:border-ink-500 hover:bg-ink-900/80'
          }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />

        {image ? (
          <div className="flex flex-col items-center gap-4 w-full">
            <div className="relative">
              <img
                src={image}
                alt="Preview"
                className="h-48 w-48 object-cover rounded-xl border border-ink-600 shadow-lg"
              />
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  setImage(null)
                  setFileName('')
                }}
                className="absolute -top-2 -right-2 h-7 w-7 rounded-full bg-ink-800 border border-ink-600 flex items-center justify-center text-mist hover:text-hazard hover:border-hazard transition-colors"
                aria-label={t.removeImage}
              >
                <ImageOff className="h-3.5 w-3.5" />
              </button>
            </div>
            <p className="font-mono text-xs text-mist truncate max-w-xs">{fileName}</p>
          </div>
        ) : (
          <>
            <div className="h-16 w-16 rounded-2xl bg-ink-800 border border-ink-600 flex items-center justify-center mb-5 transition-transform group-hover:scale-105 group-hover:border-lime/50">
              <UploadCloud className="h-7 w-7 text-lime" strokeWidth={1.75} />
            </div>
            <p className="text-paper font-medium mb-1">{t.dropHint}</p>
            <p className="text-mist text-sm">{t.dropSubHint}</p>
          </>
        )}
      </div>

      <div className="mt-8 flex flex-col items-center gap-4">
        <button
          type="button"
          disabled={!image}
          onClick={onAnalyze}
          className={`group relative inline-flex items-center gap-2.5 rounded-full px-8 py-3.5 font-semibold text-base transition-all duration-300
            ${image
              ? 'bg-lime text-ink-950 shadow-[0_0_30px_rgba(182,255,77,0.35)] hover:shadow-[0_0_45px_rgba(182,255,77,0.55)] hover:-translate-y-0.5'
              : 'bg-ink-800 text-mist/50 cursor-not-allowed border border-ink-700'
            }`}
        >
          <Sparkles className={`h-4.5 w-4.5 ${image ? 'animate-pulse' : ''}`} />
          {t.analyzeButton}
        </button>

        <div className="flex flex-wrap justify-center gap-2 font-mono text-[10px] uppercase tracking-wider text-mist/70">
          {['Vision', 'Classification', 'Localization', 'Advisory', 'Scoring'].map((tag) => (
            <span key={tag} className="border border-ink-700 rounded-full px-2.5 py-1 bg-ink-900/60">
              {tag} Agent
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

// ---------------------------------------------------------------------------
// Screen 3 — Result
// ---------------------------------------------------------------------------

function ResultScreen({ t, lang, image, result, city, onReset }) {
  const [impact, setImpact] = useState(null)
  const [impactError, setImpactError] = useState(null)
  const [disposal, setDisposal] = useState(null)
  const [disposalError, setDisposalError] = useState(null)

  useEffect(() => {
    let cancelled = false
    getUserImpact(DEFAULT_USER_ID, lang)
      .then((data) => {
        if (!cancelled) setImpact(data)
      })
      .catch((err) => {
        if (!cancelled) setImpactError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [lang])

  useEffect(() => {
    if (!result) return
    let cancelled = false

    const fetchPoints = (coords) => {
      getDisposalPoints({ lat: coords.lat, lng: coords.lng, wasteType: result.category, lang })
        .then((data) => {
          if (!cancelled) setDisposal(data)
        })
        .catch((err) => {
          if (!cancelled) setDisposalError(err.message)
        })
    }

    if (typeof navigator !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => fetchPoints({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => fetchPoints(DEFAULT_COORDS),
        { timeout: 5000 },
      )
    } else {
      fetchPoints(DEFAULT_COORDS)
    }

    return () => {
      cancelled = true
    }
  }, [result, lang])

  if (!result) return null

  const hazardLabel = result.hazard_reason || (result.is_hazardous ? t.hazardWarning : t.safeNotHazardous)

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="space-y-5"
    >
      {/* Header card: image + classification */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05, duration: 0.35 }}
        className="rounded-2xl border border-ink-700 bg-ink-900/60 p-5 sm:p-6 flex flex-col sm:flex-row gap-5"
      >
        {image && (
          <img
            src={image}
            alt={t.scannedObject}
            className="h-28 w-28 sm:h-32 sm:w-32 object-cover rounded-xl border border-ink-600 flex-shrink-0 mx-auto sm:mx-0"
          />
        )}
        <div className="flex-1 text-center sm:text-left">
          <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-mist mb-1">
            {t.classificationResult}
          </p>
          <h2 className="font-display text-3xl text-paper mb-1">{result.subcategory}</h2>
          <p className="text-mist text-sm mb-3">{result.category}</p>
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
            {result.recyclable ? (
              <Badge tone="lime" icon={Recycle}>
                {t.recyclable}
              </Badge>
            ) : (
              <Badge tone="hazard" icon={AlertTriangle}>
                {t.notRecyclable}
              </Badge>
            )}
            {result.is_hazardous ? (
              <Badge tone="hazard" icon={AlertTriangle}>
                {hazardLabel}
              </Badge>
            ) : (
              <Badge tone="emerald" icon={CheckCircle2}>
                {hazardLabel}
              </Badge>
            )}
          </div>
        </div>
      </motion.div>

      {/* Local rules strip */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.35 }}
        className="rounded-2xl border border-ink-700 bg-ink-900/60 p-4 sm:p-5 flex flex-wrap items-center gap-x-6 gap-y-3"
      >
        <div className="flex items-center gap-2.5">
          <span
            className="h-4 w-4 rounded-sm border border-ink-600 flex-shrink-0"
            style={{ backgroundColor: binColorSwatch(result.bin_color) }}
          />
          <span className="text-sm text-paper">{result.bin_color}</span>
        </div>
        <div className="h-4 w-px bg-ink-700 hidden sm:block" />
        <span className="text-sm text-mist">{result.collection_day}</span>
        <div className="h-4 w-px bg-ink-700 hidden sm:block" />
        <span className="text-sm text-mist">{city}</span>
      </motion.div>

      {/* Disposal guide */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.35 }}
        className="rounded-2xl border border-ink-700 bg-ink-900/60 p-5 sm:p-6"
      >
        <h3 className="font-display text-xl text-paper mb-4 flex items-center gap-2">
          <ListChecks className="h-5 w-5 text-lime" />
          {t.disposalGuide}
        </h3>
        <div className="space-y-3">
          {result.steps.map((step, i) => (
            <div key={i} className="flex gap-3.5">
              <div className="flex-shrink-0 h-7 w-7 rounded-full bg-lime/10 border border-lime/30 text-lime font-mono text-sm flex items-center justify-center font-semibold">
                {i + 1}
              </div>
              <p className="text-paper text-sm leading-relaxed pt-1">{step}</p>
            </div>
          ))}
        </div>

        {result.tips?.length > 0 && (
          <div className="mt-5 pt-4 border-t border-ink-700/60 space-y-2">
            {result.tips.map((tip, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-emerald/90">
                <Sparkles className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
                <span>{tip}</span>
              </div>
            ))}
          </div>
        )}

        {result.warnings?.length > 0 && (
          <div className="mt-3 pt-3 border-t border-ink-700/60 space-y-2">
            {result.warnings.map((w, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-amber/90">
                <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
                <span>{w}</span>
              </div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Impact stats */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.35 }}
        className="grid grid-cols-2 gap-4"
      >
        <StatCard
          icon={Leaf}
          label={t.co2Saved}
          value={`${result.co2_kg.toFixed(3)} kg`}
          sub={t.co2SavedSub(result.equivalent_km)}
          tone="emerald"
        />
        <StatCard
          icon={Award}
          label={t.greenPoints}
          value={`+${result.points}`}
          sub={result.badge ? t.streakWithBadge(result.streak, result.badge) : t.streakOnly(result.streak)}
          tone="lime"
        />
      </motion.div>

      {/* Cumulative user impact */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.22, duration: 0.35 }}
        className="rounded-2xl border border-ink-700 bg-ink-900/60 p-4 sm:p-5 flex items-center gap-3"
      >
        <div className="h-8 w-8 rounded-lg bg-ink-800 border border-ink-700 flex items-center justify-center text-lime flex-shrink-0">
          <Trophy className="h-4 w-4" />
        </div>
        {impact ? (
          <p className="text-sm text-mist">
            {t.totalImpactPrefix}
            <span className="text-paper">{impact.rank}</span>
            {t.totalImpactMiddle(impact.scans)}
            {impact.total_co2.toFixed(2)}
            {t.totalImpactSuffix}
          </p>
        ) : impactError ? (
          <p className="font-mono text-xs text-mist/60">{t.impactLoadError(impactError)}</p>
        ) : (
          <p className="text-sm text-mist/60">{t.impactLoading}</p>
        )}
      </motion.div>

      {/* Điểm thu gom gần nhất */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25, duration: 0.35 }}
        className="rounded-2xl border border-ink-700 bg-ink-900/60 p-5 sm:p-6"
      >
        <h3 className="font-display text-xl text-paper mb-4 flex items-center gap-2">
          <MapPin className="h-5 w-5 text-lime" />
          {t.nearestPoints}
        </h3>
        {disposal ? (
          disposal.points.length > 0 ? (
            <div className="space-y-3">
              {disposal.points.slice(0, 3).map((point, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 rounded-xl border border-ink-700 bg-ink-800/60 p-3.5"
                >
                  <div className="flex-shrink-0 h-8 w-8 rounded-lg bg-lime/10 border border-lime/30 text-lime flex items-center justify-center">
                    <MapPin className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-paper font-medium">{point.name}</p>
                    <p className="text-xs text-mist mt-0.5">{point.address}</p>
                    <p className="font-mono text-[11px] text-mist/60 mt-1">
                      {point.distance_km} km · {point.hours}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-mist">{t.noPointsFound(city)}</p>
          )
        ) : disposalError ? (
          <p className="font-mono text-xs text-mist/60">{t.pointsLoadError(disposalError)}</p>
        ) : (
          <p className="text-sm text-mist/60">{t.pointsLoading}</p>
        )}
      </motion.div>

      {/* Follow-up chat */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.35 }}
      >
        <ChatPanel t={t} lang={lang} scanContext={result} subcategory={result.subcategory} />
      </motion.div>

      <div className="flex justify-center pt-2">
        <button
          type="button"
          onClick={onReset}
          className="inline-flex items-center gap-2 rounded-full border border-ink-700 px-6 py-2.5 text-sm text-mist hover:text-paper hover:border-ink-500 transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          {t.scanAnother}
        </button>
      </div>
    </motion.div>
  )
}

function Badge({ tone, icon: Icon, children }) {
  const tones = {
    lime: 'bg-lime/10 border-lime/30 text-lime',
    emerald: 'bg-emerald/10 border-emerald/30 text-emerald',
    hazard: 'bg-hazard/10 border-hazard/30 text-hazard',
  }
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium ${tones[tone]}`}
    >
      <Icon className="h-3.5 w-3.5" />
      {children}
    </span>
  )
}

function StatCard({ icon: Icon, label, value, sub, tone }) {
  const toneColor = tone === 'lime' ? 'text-lime' : 'text-emerald'
  return (
    <div className="rounded-2xl border border-ink-700 bg-ink-900/60 p-5">
      <div className="flex items-center gap-2 mb-3">
        <div className={`h-8 w-8 rounded-lg bg-ink-800 border border-ink-700 flex items-center justify-center ${toneColor}`}>
          <Icon className="h-4 w-4" />
        </div>
        <span className="font-mono text-[11px] uppercase tracking-wider text-mist">{label}</span>
      </div>
      <p className={`font-display text-3xl ${toneColor} text-glow`}>{value}</p>
      <p className="text-xs text-mist mt-1">{sub}</p>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Follow-up chat panel — gọi POST /api/chat (Advisory Agent)
// ---------------------------------------------------------------------------

function ChatPanel({ t, lang, scanContext, subcategory }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: t.chatGreeting(subcategory),
    },
  ])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, typing])

  const handleSend = async () => {
    const question = input.trim()
    if (!question || typing) return
    setMessages((prev) => [...prev, { role: 'user', text: question }])
    setInput('')
    setTyping(true)
    try {
      const data = await sendChatMessage({ question, scanContext, lang })
      setMessages((prev) => [...prev, { role: 'assistant', text: data.answer }])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: t.chatError(err.message) },
      ])
    } finally {
      setTyping(false)
    }
  }

  return (
    <div className="rounded-2xl border border-ink-700 bg-ink-900/60 overflow-hidden">
      <div className="flex items-center gap-2 px-5 py-3 border-b border-ink-700 bg-ink-800/50">
        <Bot className="h-4 w-4 text-lime" />
        <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-mist">
          {t.askAdvisory}
        </span>
      </div>

      <div ref={scrollRef} className="max-h-64 overflow-y-auto scrollbar-thin px-5 py-4 space-y-3">
        {messages.map((m, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
            className={`flex gap-2.5 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div
              className={`flex-shrink-0 h-7 w-7 rounded-full flex items-center justify-center border
              ${m.role === 'user' ? 'bg-lime/10 border-lime/30 text-lime' : 'bg-ink-800 border-ink-700 text-emerald'}`}
            >
              {m.role === 'user' ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
            </div>
            <div
              className={`rounded-2xl px-3.5 py-2 text-sm leading-relaxed max-w-[85%]
              ${m.role === 'user'
                ? 'bg-lime/10 border border-lime/20 text-paper rounded-tr-sm'
                : 'bg-ink-800 border border-ink-700 text-mist rounded-tl-sm'}`}
            >
              {m.text}
            </div>
          </motion.div>
        ))}

        {typing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-2.5"
          >
            <div className="flex-shrink-0 h-7 w-7 rounded-full flex items-center justify-center border bg-ink-800 border-ink-700 text-emerald">
              <Bot className="h-3.5 w-3.5" />
            </div>
            <div className="rounded-2xl rounded-tl-sm px-4 py-2.5 bg-ink-800 border border-ink-700 flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-mist animate-bounce [animation-delay:-0.3s]" />
              <span className="h-1.5 w-1.5 rounded-full bg-mist animate-bounce [animation-delay:-0.15s]" />
              <span className="h-1.5 w-1.5 rounded-full bg-mist animate-bounce" />
            </div>
          </motion.div>
        )}
      </div>

      <div className="flex items-center gap-2 px-4 py-3 border-t border-ink-700">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={t.chatPlaceholder}
          className="flex-1 bg-ink-800 border border-ink-700 rounded-full px-4 py-2 text-sm text-paper placeholder:text-mist/50 focus:outline-none focus:border-lime/50 transition-colors"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={!input.trim() || typing}
          className={`flex-shrink-0 h-9 w-9 rounded-full flex items-center justify-center transition-colors
            ${input.trim() && !typing
              ? 'bg-lime text-ink-950 hover:shadow-[0_0_20px_rgba(182,255,77,0.5)]'
              : 'bg-ink-800 border border-ink-700 text-mist/40 cursor-not-allowed'}`}
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
