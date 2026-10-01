import { useState, useEffect, useCallback } from "react"
import { useParams, useSearchParams, useNavigate } from "react-router-dom"
import { motion, AnimatePresence } from "framer-motion"
import {
  AlertTriangle, CheckCircle, Leaf, Droplets, Sprout,
  ShieldAlert, BarChart2, BookOpen, ChevronDown, ChevronUp,
  Info, FlaskConical, ArrowLeft, Star, ExternalLink,
  AlertCircle, Zap, Bug, RefreshCw, Heart, CircleHelp
} from "lucide-react"
import { API_BASE_URL } from "../services/api"

// ─────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────
interface Source {
  source_type: string
  source_title: string
  source_url: string
  source_date?: string
}

interface RecommendationCard {
  id: string
  title: string
  description: string
  why_it_matters: string
  priority: string
  applicable_condition: string
  source?: Source
}

interface GuidanceData {
  analysis_id: string
  knowledge_base_version: string
  crop: string
  growth_stage: string
  environment: string
  predicted_class: string
  confidence: number
  confidence_level: string
  is_confirmed: boolean
  status_label: string
  health_status: string
  health_indicator_score: number
  severity_percentage: number
  severity_level: string
  severity_interpretation: string
  immediate_actions: RecommendationCard[]
  prevention: RecommendationCard[]
  water_and_environment: RecommendationCard[]
  nutrition_guidance: RecommendationCard[]
  natural_and_biological_options: RecommendationCard[]
  what_to_avoid: RecommendationCard[]
  disease_vs_nutrient_note: string
  chemical_management_reference?: string
  resistance_management_note?: string
  integrated_pest_management_note: string
  monitoring_interval_days: number
  recommended_next_check: string
  when_to_seek_expert_advice: string[]
  sources: Source[]
  disclaimer: string
}

// ─────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────
const PRIORITY_COLORS: Record<string, string> = {
  Immediate: "border-red-500/50 bg-red-500/5",
  High: "border-orange-400/50 bg-orange-400/5",
  Medium: "border-yellow-400/50 bg-yellow-400/5",
  Preventive: "border-emerald-500/50 bg-emerald-500/5",
  Informational: "border-blue-400/50 bg-blue-400/5",
}

const PRIORITY_BADGE: Record<string, string> = {
  Immediate: "bg-red-500/20 text-red-400",
  High: "bg-orange-400/20 text-orange-400",
  Medium: "bg-yellow-400/20 text-yellow-400",
  Preventive: "bg-emerald-500/20 text-emerald-400",
  Informational: "bg-blue-400/20 text-blue-400",
}

function HealthIndicatorRing({ score }: { score: number }) {
  const colour = score >= 75 ? "#10b981" : score >= 50 ? "#f59e0b" : "#ef4444"
  const stroke = 8
  const r = 44
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ

  return (
    <div className="relative w-28 h-28 flex items-center justify-center">
      <svg width="112" height="112" className="-rotate-90">
        <circle cx="56" cy="56" r={r} strokeWidth={stroke} className="fill-none stroke-white/5" />
        <circle
          cx="56" cy="56" r={r}
          strokeWidth={stroke}
          fill="none"
          stroke={colour}
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s ease" }}
        />
      </svg>
      <div className="absolute text-center">
        <span className="text-2xl font-bold" style={{ color: colour }}>{score}</span>
        <span className="block text-[10px] text-gray-400 mt-0.5">/ 100</span>
      </div>
    </div>
  )
}

function CardGroup({
  title, icon, cards, defaultOpen = true, accentClass = "text-emerald-400"
}: {
  title: string
  icon: React.ReactNode
  cards: RecommendationCard[]
  defaultOpen?: boolean
  accentClass?: string
}) {
  const [open, setOpen] = useState(defaultOpen)
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set())

  if (!cards || cards.length === 0) return null

  const toggleCard = (id: string) => {
    setExpandedCards(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-white/8 bg-white/3 backdrop-blur-sm overflow-hidden"
    >
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-white/4 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className={accentClass}>{icon}</span>
          <span className="font-semibold text-gray-100">{title}</span>
          <span className="text-xs bg-white/8 text-gray-400 px-2 py-0.5 rounded-full">{cards.length}</span>
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="px-4 pb-4 space-y-3"
          >
            {cards.map(card => (
              <div
                key={card.id}
                className={`rounded-xl border p-4 transition-all ${PRIORITY_COLORS[card.priority] || "border-white/8 bg-white/3"}`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${PRIORITY_BADGE[card.priority] || "bg-white/10 text-gray-400"}`}>
                        {card.priority}
                      </span>
                      {card.applicable_condition && (
                        <span className="text-[10px] text-gray-500 truncate max-w-[200px]">{card.applicable_condition}</span>
                      )}
                    </div>
                    <p className="text-sm font-semibold text-gray-100 mb-1">{card.title}</p>
                    <p className="text-sm text-gray-400">{card.description}</p>
                  </div>
                  <button
                    onClick={() => toggleCard(card.id)}
                    className="text-gray-600 hover:text-gray-400 mt-0.5 shrink-0"
                  >
                    {expandedCards.has(card.id) ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>

                <AnimatePresence>
                  {expandedCards.has(card.id) && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="mt-3 pt-3 border-t border-white/8 space-y-2"
                    >
                      {card.why_it_matters && (
                        <div className="flex gap-2">
                          <Info className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
                          <p className="text-xs text-gray-400"><span className="text-blue-400 font-medium">Why it matters:</span> {card.why_it_matters}</p>
                        </div>
                      )}
                      {card.source && (
                        <div className="flex gap-2 items-center">
                          <BookOpen className="w-3.5 h-3.5 text-gray-600 shrink-0" />
                          <a
                            href={card.source.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-emerald-400/80 hover:text-emerald-400 flex items-center gap-1 transition-colors"
                          >
                            {card.source.source_title}
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// ─────────────────────────────────────────────────────────────────────
// Main Guidance Page
// ─────────────────────────────────────────────────────────────────────
export default function GuidancePage() {
  const { analysis_id } = useParams<{ analysis_id: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const [guidance, setGuidance] = useState<GuidanceData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Crop selection form
  const [crop, setCrop] = useState(searchParams.get("crop") || "")
  const [growthStage, setGrowthStage] = useState("")
  const [environment, setEnvironment] = useState("unspecified")
  const [submitted, setSubmitted] = useState(false)

  const SUPPORTED_CROPS = ["Tomato", "Potato", "Apple", "Corn", "Grape", "Pepper"]

  const fetchGuidance = useCallback(async (cropValue: string) => {
    if (!analysis_id) return
    setLoading(true)
    setError(null)
    try {
      const resp = await fetch(`${API_BASE_URL}/api/guidance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          analysis_id,
          crop: cropValue || null,
          growth_stage: growthStage || "unspecified",
          environment: environment || "unspecified"
        })
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(err.detail || `Server error ${resp.status}`)
      }
      const data = await resp.json()
      setGuidance(data)
    } catch (e: any) {
      setError(e.message || "Failed to load guidance.")
    } finally {
      setLoading(false)
    }
  }, [analysis_id, growthStage, environment])

  // Auto-load if crop already known from query param
  useEffect(() => {
    const paramCrop = searchParams.get("crop")
    if (paramCrop && analysis_id) {
      setCrop(paramCrop)
      setSubmitted(true)
      fetchGuidance(paramCrop)
    }
  }, [analysis_id])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
    fetchGuidance(crop)
  }

  const statusColor = (status: string) => {
    if (status.includes("Healthy")) return "text-emerald-400"
    if (status.includes("Expert")) return "text-red-400"
    if (status.includes("Attention")) return "text-orange-400"
    return "text-yellow-400"
  }

  const statusIcon = (status: string) => {
    if (status.includes("Healthy")) return <CheckCircle className="w-5 h-5 text-emerald-400" />
    if (status.includes("Expert")) return <AlertTriangle className="w-5 h-5 text-red-400" />
    if (status.includes("Attention")) return <AlertCircle className="w-5 h-5 text-orange-400" />
    return <RefreshCw className="w-5 h-5 text-yellow-400" />
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto pb-16">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-300 transition-colors mb-4"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 flex items-center justify-center">
            <Heart className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-100">Plant Health Guidance</h1>
            <p className="text-sm text-gray-500">
              Analysis: <span className="text-gray-400 font-mono text-xs">{analysis_id}</span>
            </p>
          </div>
        </div>
      </motion.div>

      {/* Crop Selection Form */}
      {!submitted && (
        <motion.form
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          onSubmit={handleSubmit}
          className="rounded-2xl border border-white/10 bg-white/4 backdrop-blur-sm p-6 space-y-5"
        >
          <div className="flex items-center gap-3 mb-1">
            <Sprout className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-semibold text-gray-100">Select Your Crop</h2>
          </div>
          <p className="text-sm text-gray-500">
            Crop information enables more relevant guidance. Without a crop, generic guidance is provided.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">Crop <span className="text-gray-600">(required for specific guidance)</span></label>
              <select
                value={crop}
                onChange={e => setCrop(e.target.value)}
                className="w-full bg-white/6 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
              >
                <option value="">— Select crop —</option>
                {SUPPORTED_CROPS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
              <p className="text-xs text-gray-600 mt-1">Supported crops. Additional crops can be added to the knowledge base.</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">Growth Stage <span className="text-gray-600">(optional)</span></label>
              <input
                type="text"
                placeholder="e.g. Flowering, Vegetative"
                value={growthStage}
                onChange={e => setGrowthStage(e.target.value)}
                className="w-full bg-white/6 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">Growing Environment <span className="text-gray-600">(optional)</span></label>
              <select
                value={environment}
                onChange={e => setEnvironment(e.target.value)}
                className="w-full bg-white/6 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
              >
                <option value="unspecified">Unspecified</option>
                <option value="field">Field / Outdoor</option>
                <option value="greenhouse">Greenhouse</option>
                <option value="indoor">Indoor</option>
                <option value="container">Container / Pot</option>
              </select>
            </div>
          </div>

          <div className="flex gap-3 pt-1">
            <button
              type="submit"
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-lg transition-colors"
            >
              Get Plant Health Guidance
            </button>
            <button
              type="button"
              onClick={() => { setSubmitted(true); fetchGuidance("") }}
              className="px-5 py-2.5 bg-white/6 hover:bg-white/10 text-gray-400 text-sm rounded-lg transition-colors"
            >
              Skip — Use Generic Guidance
            </button>
          </div>
        </motion.form>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 rounded-full border-2 border-emerald-500/30 border-t-emerald-500 animate-spin" />
            <p className="text-sm text-gray-500">Generating plant health guidance…</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-5 flex gap-3 items-start">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-red-400 mb-1">Failed to load guidance</p>
            <p className="text-sm text-gray-400">{error}</p>
            <button onClick={() => fetchGuidance(crop)} className="mt-3 text-xs text-emerald-400 hover:underline">
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Guidance Content */}
      {guidance && !loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          {/* 1. Diagnosis Summary */}
          <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/4 to-white/2 backdrop-blur-sm p-5">
            <div className="flex flex-col sm:flex-row gap-5 items-start sm:items-center justify-between">
              <div className="flex-1 space-y-3">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded-full ${guidance.is_confirmed ? "bg-emerald-500/20 text-emerald-400" : "bg-yellow-500/20 text-yellow-400"}`}>
                    {guidance.status_label}
                  </span>
                  <span className="text-xs bg-white/8 text-gray-500 px-2 py-0.5 rounded-full">
                    KB {guidance.knowledge_base_version}
                  </span>
                </div>

                <div>
                  <p className="text-xs text-gray-500 mb-0.5">Possible Condition</p>
                  <h2 className="text-xl font-bold text-gray-100">{guidance.predicted_class}</h2>
                  <p className="text-sm text-gray-500 mt-1">Crop: <span className="text-gray-300">{guidance.crop}</span></p>
                </div>

                <div className="flex flex-wrap gap-3">
                  <div className="bg-white/6 rounded-lg px-3 py-2 text-center">
                    <p className="text-xs text-gray-500">Confidence</p>
                    <p className={`text-lg font-bold ${guidance.confidence_level === "high" ? "text-emerald-400" : guidance.confidence_level === "medium" ? "text-yellow-400" : "text-red-400"}`}>
                      {(guidance.confidence * 100).toFixed(1)}%
                    </p>
                    <p className="text-[10px] text-gray-600 capitalize">{guidance.confidence_level}</p>
                  </div>
                  <div className="bg-white/6 rounded-lg px-3 py-2 text-center">
                    <p className="text-xs text-gray-500">Visible Severity</p>
                    <p className={`text-lg font-bold ${guidance.severity_percentage < 15 ? "text-emerald-400" : guidance.severity_percentage < 35 ? "text-yellow-400" : "text-red-400"}`}>
                      {guidance.severity_percentage.toFixed(1)}%
                    </p>
                    <p className="text-[10px] text-gray-600">{guidance.severity_level}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {statusIcon(guidance.health_status)}
                  <span className={`text-sm font-medium ${statusColor(guidance.health_status)}`}>{guidance.health_status}</span>
                </div>
              </div>

              <div className="flex flex-col items-center gap-1">
                <HealthIndicatorRing score={guidance.health_indicator_score} />
                <p className="text-xs text-gray-500 text-center">Plant Health<br />Indicator</p>
                <p className="text-[10px] text-gray-700 text-center max-w-[120px]">Not a clinical metric. Based on visible severity + confidence.</p>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-white/8">
              <p className="text-xs text-gray-500">{guidance.severity_interpretation}</p>
            </div>
          </div>

          {/* Low confidence warning banner */}
          {guidance.confidence_level === "low" && (
            <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/5 p-4 flex gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-yellow-300 mb-1">Low Prediction Confidence</p>
                <p className="text-sm text-gray-400">
                  Prediction confidence is low. The image may not match the supported disease classes.
                  Please provide another clear image or consult an agricultural expert.
                </p>
              </div>
            </div>
          )}

          {/* 2. Immediate Actions */}
          <CardGroup
            title="What To Do Now"
            icon={<Zap className="w-5 h-5" />}
            cards={guidance.immediate_actions}
            accentClass="text-red-400"
          />

          {/* 3. Prevention */}
          <CardGroup
            title="Prevent Further Spread"
            icon={<ShieldAlert className="w-5 h-5" />}
            cards={guidance.prevention}
            accentClass="text-emerald-400"
          />

          {/* 4. Water & Environment */}
          <CardGroup
            title="Water & Irrigation Guidance"
            icon={<Droplets className="w-5 h-5" />}
            cards={guidance.water_and_environment}
            accentClass="text-blue-400"
          />

          {/* 5. Nutrition Guidance */}
          <CardGroup
            title="Nutrition Guidance"
            icon={<Sprout className="w-5 h-5" />}
            cards={guidance.nutrition_guidance}
            defaultOpen={false}
            accentClass="text-lime-400"
          />

          {/* 6. Natural & Biological Options */}
          <CardGroup
            title="Natural & Biological Options"
            icon={<Leaf className="w-5 h-5" />}
            cards={guidance.natural_and_biological_options}
            defaultOpen={false}
            accentClass="text-teal-400"
          />

          {/* 7. What To Avoid */}
          <CardGroup
            title="What To Avoid"
            icon={<Bug className="w-5 h-5" />}
            cards={guidance.what_to_avoid}
            defaultOpen={false}
            accentClass="text-orange-400"
          />

          {/* 8. Disease vs Nutrient Note */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border border-blue-400/20 bg-blue-400/5 p-5"
          >
            <div className="flex items-center gap-2 mb-3">
              <Info className="w-4 h-4 text-blue-400" />
              <h3 className="text-sm font-semibold text-blue-300">Educational Note: Disease vs. Nutrient Deficiency</h3>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">{guidance.disease_vs_nutrient_note}</p>
          </motion.div>

          {/* 9. Monitoring Plan */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5"
          >
            <div className="flex items-center gap-2 mb-3">
              <BarChart2 className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold text-emerald-300">Monitoring Plan</h3>
            </div>
            <div className="flex flex-wrap gap-4 mb-3">
              <div className="bg-white/5 rounded-lg px-4 py-2 text-center">
                <p className="text-xs text-gray-500">Recommended Interval</p>
                <p className="text-xl font-bold text-emerald-400">{guidance.monitoring_interval_days}</p>
                <p className="text-xs text-gray-600">days</p>
              </div>
            </div>
            <p className="text-sm text-gray-400">{guidance.recommended_next_check}</p>
            <p className="text-xs text-gray-600 mt-2">
              This interval is derived from the disease knowledge base. Always recheck sooner if symptoms worsen.
            </p>
          </motion.div>

          {/* 10. IPM Strategy */}
          {guidance.integrated_pest_management_note && (
            <details className="rounded-2xl border border-white/8 bg-white/3 overflow-hidden">
              <summary className="px-5 py-4 cursor-pointer text-sm font-semibold text-gray-300 flex items-center gap-2 hover:bg-white/4 transition-colors">
                <FlaskConical className="w-4 h-4 text-purple-400" />
                Integrated Plant Health Strategy (IPM)
              </summary>
              <div className="px-5 pb-4">
                <p className="text-sm text-gray-400 leading-relaxed">{guidance.integrated_pest_management_note}</p>
                {guidance.chemical_management_reference && (
                  <div className="mt-3 pt-3 border-t border-white/8">
                    <p className="text-xs text-gray-500 mb-1 font-medium">Chemical Management Reference</p>
                    <p className="text-xs text-gray-400">{guidance.chemical_management_reference}</p>
                  </div>
                )}
                {guidance.resistance_management_note && (
                  <div className="mt-3 pt-3 border-t border-white/8">
                    <p className="text-xs text-gray-500 mb-1 font-medium">Resistance Management</p>
                    <p className="text-xs text-gray-400">{guidance.resistance_management_note}</p>
                  </div>
                )}
              </div>
            </details>
          )}

          {/* 11. Expert Review */}
          {guidance.when_to_seek_expert_advice && guidance.when_to_seek_expert_advice.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl border border-red-500/20 bg-red-500/5 p-5"
            >
              <div className="flex items-center gap-2 mb-3">
                <CircleHelp className="w-4 h-4 text-red-400" />
                <h3 className="text-sm font-semibold text-red-300">When To Seek Expert Advice</h3>
              </div>
              <p className="text-xs text-gray-500 mb-3">Consider consulting a qualified agronomist or plant pathologist in these situations:</p>
              <ul className="space-y-2">
                {guidance.when_to_seek_expert_advice.map((cond, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-400">
                    <span className="text-red-400 mt-0.5 shrink-0">•</span>
                    {cond}
                  </li>
                ))}
              </ul>
            </motion.div>
          )}

          {/* 12. Sources */}
          {guidance.sources && guidance.sources.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl border border-white/8 bg-white/3 p-5"
            >
              <div className="flex items-center gap-2 mb-4">
                <BookOpen className="w-4 h-4 text-gray-400" />
                <h3 className="text-sm font-semibold text-gray-300">Guidance Sources</h3>
              </div>
              <div className="space-y-3">
                {guidance.sources.map((src, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <Star className="w-3.5 h-3.5 text-gray-600 shrink-0 mt-0.5" />
                    <div>
                      <a
                        href={src.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-emerald-400/80 hover:text-emerald-400 flex items-center gap-1 transition-colors"
                      >
                        {src.source_title}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                      <p className="text-[10px] text-gray-600 capitalize">{src.source_type.replace(/_/g, " ")} {src.source_date ? `— ${src.source_date}` : ""}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Disclaimer */}
          <div className="rounded-xl border border-white/6 bg-white/2 p-4">
            <p className="text-[11px] text-gray-600 leading-relaxed">{guidance.disclaimer}</p>
            <p className="text-[11px] text-gray-700 mt-2">
              Natural options do not automatically mean risk-free. Follow crop-specific guidance and product labels where applicable.
            </p>
          </div>

          {/* Change Crop Button */}
          <div className="flex justify-end">
            <button
              onClick={() => { setSubmitted(false); setGuidance(null) }}
              className="text-sm text-gray-500 hover:text-gray-300 flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Change crop or growth stage
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
