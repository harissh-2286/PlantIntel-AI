import { useState, useEffect, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { motion, AnimatePresence } from "framer-motion"
import {
  Leaf, Plus, Clock, AlertTriangle,
  RefreshCw, Trash2, X,
  Activity, TrendingUp, TrendingDown,
  Minus, Info, ArrowRight, Eye, LineChart, GitCompare
} from "lucide-react"
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip
} from "recharts"
import { API_BASE_URL } from "../services/api"

// ─────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────
interface PlantItem {
  plant_id: string
  name: string
  crop: string
  variety?: string
  created_at: string
  last_scan_at?: string
  health_status: string
  latest_disease?: string
  latest_confidence?: number
  latest_severity?: number
  analysis_count: number
}

interface TimelineEvent {
  timeline_day: string
  timestamp: string
  analysis_id: string
  disease: string
  confidence: number
  severity_percentage: number
  severity_level: string
  affected_area_pixels: number
  image_url?: string
}

interface TrendPoint {
  timestamp: string
  label: string
  severity_percentage: number
  confidence: number
  disease: string
}

interface TrendData {
  plant_id: string
  plant_name: string
  crop: string
  trend_label: string
  data_points: TrendPoint[]
  overall_direction: string
  disclaimer: string
}

interface DashboardData {
  total_plants_monitored: number
  recently_analyzed: any[]
  health_status_distribution: Record<string, number>
  low_confidence_cases: number
  expert_review_recommended_count: number
  attention_recommended_count: number
}

// ─────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────
const STATUS_COLORS: Record<string, { border: string; bg: string; text: string; dot: string }> = {
  "Healthy / No supported disease detected": { border: "border-emerald-500/40", bg: "bg-emerald-500/8", text: "text-emerald-400", dot: "bg-emerald-400" },
  "Monitor": { border: "border-yellow-400/40", bg: "bg-yellow-400/8", text: "text-yellow-400", dot: "bg-yellow-400" },
  "Attention Recommended": { border: "border-orange-400/40", bg: "bg-orange-400/8", text: "text-orange-400", dot: "bg-orange-400" },
  "Expert Review Recommended": { border: "border-red-500/40", bg: "bg-red-500/8", text: "text-red-400", dot: "bg-red-400" },
}
const getStatus = (s: string) => STATUS_COLORS[s] || STATUS_COLORS["Monitor"]

function formatDate(iso: string) {
  if (!iso) return "—"
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })
}

function formatRelative(iso: string) {
  if (!iso) return "—"
  const now = Date.now()
  const ms = now - new Date(iso).getTime()
  const days = Math.floor(ms / 86400000)
  if (days === 0) return "Today"
  if (days === 1) return "Yesterday"
  return `${days}d ago`
}

function TrendIcon({ direction }: { direction: string }) {
  if (direction === "improving") return <TrendingDown className="w-4 h-4 text-emerald-400" />
  if (direction === "worsening") return <TrendingUp className="w-4 h-4 text-red-400" />
  return <Minus className="w-4 h-4 text-yellow-400" />
}

// ─────────────────────────────────────────────────────────────────────
// Trend Chart
// ─────────────────────────────────────────────────────────────────────
function TrendChart({ trend }: { trend: TrendData }) {
  if (!trend.data_points || trend.data_points.length < 2) {
    return (
      <div className="flex items-center justify-center py-10 text-gray-600 text-sm">
        <Info className="w-4 h-4 mr-2" /> Not enough scans to display trend (need at least 2)
      </div>
    )
  }

  const data = trend.data_points.map(p => ({
    name: p.label,
    severity: parseFloat(p.severity_percentage.toFixed(1)),
    confidence: parseFloat((p.confidence * 100).toFixed(1)),
  }))

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <TrendIcon direction={trend.overall_direction} />
        <span className="text-sm text-gray-400 capitalize">{trend.overall_direction.replace("_", " ")}</span>
        <span className="text-xs text-gray-600 ml-auto">{trend.trend_label}</span>
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
          <defs>
            <linearGradient id="sevGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} axisLine={false} tickLine={false} domain={[0, 100]} />
          <Tooltip
            contentStyle={{ background: "#1a1f24", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }}
            labelStyle={{ color: "#d1d5db", fontSize: 12 }}
            itemStyle={{ color: "#f59e0b", fontSize: 12 }}
            formatter={(val: unknown) => [`${Number(val).toFixed(1)}%`, "Visible Severity"]}
          />
          <Area type="monotone" dataKey="severity" stroke="#f59e0b" fill="url(#sevGrad)" strokeWidth={2} dot={{ r: 4, fill: "#f59e0b", strokeWidth: 0 }} />
        </AreaChart>
      </ResponsiveContainer>
      <p className="text-[10px] text-gray-700 leading-relaxed">{trend.disclaimer}</p>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────
// Plant Card
// ─────────────────────────────────────────────────────────────────────
function PlantCard({ plant, onDelete, onSelect, selected }: {
  plant: PlantItem
  onDelete: (id: string) => void
  onSelect: (id: string) => void
  selected: boolean
}) {
  const st = getStatus(plant.health_status)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      className={`rounded-2xl border ${st.border} ${st.bg} backdrop-blur-sm p-4 cursor-pointer transition-all hover:bg-white/5 ${selected ? "ring-2 ring-emerald-500/40" : ""}`}
      onClick={() => onSelect(plant.plant_id)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${st.dot} animate-pulse`} />
          <span className={`text-xs font-semibold ${st.text}`}>{plant.health_status}</span>
        </div>
        <button
          onClick={e => { e.stopPropagation(); onDelete(plant.plant_id) }}
          className="text-gray-700 hover:text-red-400 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>

      <h3 className="font-semibold text-gray-100 mb-0.5">{plant.name}</h3>
      <p className="text-xs text-gray-500 mb-3">{plant.crop}{plant.variety ? ` — ${plant.variety}` : ""}</p>

      {plant.latest_disease && (
        <p className="text-xs text-gray-400 mb-1 truncate">
          {plant.latest_disease.replace(/___/g, " - ").replace(/_/g, " ")}
        </p>
      )}

      <div className="flex items-center gap-3 mt-2">
        {plant.latest_severity !== undefined && plant.latest_severity !== null && (
          <div className="text-center">
            <p className="text-[10px] text-gray-600">Severity</p>
            <p className={`text-sm font-bold ${plant.latest_severity < 15 ? "text-emerald-400" : plant.latest_severity < 35 ? "text-yellow-400" : "text-red-400"}`}>
              {plant.latest_severity.toFixed(1)}%
            </p>
          </div>
        )}
        {plant.latest_confidence !== undefined && plant.latest_confidence !== null && (
          <div className="text-center">
            <p className="text-[10px] text-gray-600">Confidence</p>
            <p className="text-sm font-bold text-gray-300">{(plant.latest_confidence * 100).toFixed(0)}%</p>
          </div>
        )}
        <div className="text-center ml-auto">
          <p className="text-[10px] text-gray-600">Scans</p>
          <p className="text-sm font-bold text-gray-300">{plant.analysis_count}</p>
        </div>
      </div>

      {plant.last_scan_at && (
        <div className="flex items-center gap-1 mt-3 pt-2 border-t border-white/6">
          <Clock className="w-3 h-3 text-gray-600" />
          <span className="text-[10px] text-gray-600">Last scan: {formatRelative(plant.last_scan_at)}</span>
        </div>
      )}
    </motion.div>
  )
}

// ─────────────────────────────────────────────────────────────────────
// Add Plant Modal
// ─────────────────────────────────────────────────────────────────────
function AddPlantModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [form, setForm] = useState({
    name: "", crop: "Tomato", variety: "", growth_stage: "unspecified",
    environment: "field", soil_type: "", irrigation_method: "", location: "",
    notes: "", initial_analysis_id: ""
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const CROPS = ["Tomato", "Potato", "Apple", "Corn", "Grape", "Pepper"]

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const resp = await fetch(`${API_BASE_URL}/api/plants`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name,
          crop: form.crop,
          variety: form.variety || null,
          growth_stage: form.growth_stage || "unspecified",
          environment: form.environment || "unspecified",
          soil_type: form.soil_type || null,
          irrigation_method: form.irrigation_method || null,
          location: form.location || null,
          notes: form.notes || null,
          initial_analysis_id: form.initial_analysis_id || null
        })
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(err.detail || "Failed to create plant profile.")
      }
      onCreated()
      onClose()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-[#1a1f24] border border-white/10 rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between p-5 border-b border-white/8">
          <div className="flex items-center gap-3">
            <Leaf className="w-5 h-5 text-emerald-400" />
            <h2 className="font-semibold text-gray-100">Add Plant Profile</h2>
          </div>
          <button onClick={onClose} className="text-gray-600 hover:text-gray-300 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleCreate} className="p-5 space-y-4">
          {error && <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg p-3">{error}</div>}

          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="text-xs text-gray-500 mb-1 block">Plant / Field Name *</label>
              <input required value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                placeholder="e.g. Greenhouse Row 3" className="input-field" />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Crop *</label>
              <select value={form.crop} onChange={e => setForm(f => ({ ...f, crop: e.target.value }))} className="input-field">
                {CROPS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Variety (optional)</label>
              <input value={form.variety} onChange={e => setForm(f => ({ ...f, variety: e.target.value }))}
                placeholder="e.g. Beefsteak" className="input-field" />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Growth Stage</label>
              <input value={form.growth_stage} onChange={e => setForm(f => ({ ...f, growth_stage: e.target.value }))}
                placeholder="e.g. Flowering" className="input-field" />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Environment</label>
              <select value={form.environment} onChange={e => setForm(f => ({ ...f, environment: e.target.value }))} className="input-field">
                <option value="field">Field / Outdoor</option>
                <option value="greenhouse">Greenhouse</option>
                <option value="indoor">Indoor</option>
                <option value="container">Container</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Location (optional)</label>
              <input value={form.location} onChange={e => setForm(f => ({ ...f, location: e.target.value }))}
                placeholder="e.g. Field Block A" className="input-field" />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">Soil Type (optional)</label>
              <input value={form.soil_type} onChange={e => setForm(f => ({ ...f, soil_type: e.target.value }))}
                placeholder="e.g. Sandy loam" className="input-field" />
            </div>
            <div className="col-span-2">
              <label className="text-xs text-gray-500 mb-1 block">Initial Analysis ID (optional)</label>
              <input value={form.initial_analysis_id} onChange={e => setForm(f => ({ ...f, initial_analysis_id: e.target.value }))}
                placeholder="e.g. PI-20250101-ABCDEF (link first scan)" className="input-field font-mono text-xs" />
            </div>
            <div className="col-span-2">
              <label className="text-xs text-gray-500 mb-1 block">Notes (optional)</label>
              <textarea value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                rows={2} placeholder="Any additional notes…" className="input-field resize-none" />
            </div>
          </div>

          <div className="flex gap-3 pt-1">
            <button type="submit" disabled={loading}
              className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors">
              {loading ? "Creating…" : "Create Plant Profile"}
            </button>
            <button type="button" onClick={onClose}
              className="px-5 py-2.5 bg-white/6 hover:bg-white/10 text-gray-400 text-sm rounded-lg transition-colors">
              Cancel
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────
// Link Analysis Modal
// ─────────────────────────────────────────────────────────────────────
function LinkAnalysisModal({ plantId, onClose, onLinked }: {
  plantId: string
  onClose: () => void
  onLinked: () => void
}) {
  const [analysisId, setAnalysisId] = useState("")
  const [notes, setNotes] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleLink = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const resp = await fetch(`${API_BASE_URL}/api/plants/${plantId}/analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis_id: analysisId, notes: notes || null })
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(err.detail || "Failed to link analysis.")
      }
      onLinked()
      onClose()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-[#1a1f24] border border-white/10 rounded-2xl w-full max-w-md"
      >
        <div className="flex items-center justify-between p-5 border-b border-white/8">
          <h2 className="font-semibold text-gray-100 flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400" /> Link Analysis Scan
          </h2>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-600" /></button>
        </div>
        <form onSubmit={handleLink} className="p-5 space-y-4">
          {error && <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg p-3">{error}</div>}
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Analysis ID *</label>
            <input required value={analysisId} onChange={e => setAnalysisId(e.target.value)}
              placeholder="e.g. PI-20250101-ABCDEF" className="input-field font-mono text-xs w-full" />
            <p className="text-[10px] text-gray-600 mt-1">Find Analysis IDs in the History page.</p>
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Notes (optional)</label>
            <input value={notes} onChange={e => setNotes(e.target.value)}
              placeholder="e.g. After rain event" className="input-field w-full" />
          </div>
          <div className="flex gap-3">
            <button type="submit" disabled={loading}
              className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors">
              {loading ? "Linking…" : "Link Analysis"}
            </button>
            <button type="button" onClick={onClose}
              className="px-5 py-2.5 bg-white/6 hover:bg-white/10 text-gray-400 text-sm rounded-lg transition-colors">
              Cancel
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────
// Plant Detail Panel
// ─────────────────────────────────────────────────────────────────────
function PlantDetailPanel({ plantId, onClose, onRefresh }: {
  plantId: string
  onClose: () => void
  onRefresh: () => void
}) {
  const navigate = useNavigate()
  const [detail, setDetail] = useState<any>(null)
  const [trend, setTrend] = useState<TrendData | null>(null)
  const [loading, setLoading] = useState(true)
  const [showLinkModal, setShowLinkModal] = useState(false)
  const [compareA, setCompareA] = useState("")
  const [compareB, setCompareB] = useState("")
  const [comparison, setComparison] = useState<any>(null)

  const loadDetail = useCallback(async () => {
    setLoading(true)
    try {
      const [detailResp, trendResp] = await Promise.all([
        fetch(`${API_BASE_URL}/api/plants/${plantId}`),
        fetch(`${API_BASE_URL}/api/plants/${plantId}/trend`)
      ])
      if (detailResp.ok) setDetail(await detailResp.json())
      if (trendResp.ok) setTrend(await trendResp.json())
    } catch {}
    setLoading(false)
  }, [plantId])

  useEffect(() => { loadDetail() }, [loadDetail])

  const handleCompare = async () => {
    if (!compareA || !compareB) return
    try {
      const resp = await fetch(`${API_BASE_URL}/api/plants/${plantId}/compare?scan_a=${compareA}&scan_b=${compareB}`)
      if (resp.ok) setComparison(await resp.json())
    } catch {}
  }

  if (loading) return (
    <div className="flex items-center justify-center py-16">
      <div className="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
    </div>
  )

  if (!detail) return (
    <div className="py-10 text-center text-gray-600">Failed to load plant detail.</div>
  )

  const st = getStatus(detail.health_status)
  const timeline: TimelineEvent[] = detail.timeline || []
  const alerts: any[] = detail.alerts || []

  return (
    <div className="space-y-5">
      {showLinkModal && (
        <LinkAnalysisModal
          plantId={plantId}
          onClose={() => setShowLinkModal(false)}
          onLinked={() => { loadDetail(); onRefresh() }}
        />
      )}

      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-bold text-lg text-gray-100">{detail.name}</h2>
          <p className="text-sm text-gray-500">{detail.crop}{detail.variety ? ` — ${detail.variety}` : ""}</p>
        </div>
        <button onClick={onClose} className="text-gray-600 hover:text-gray-400 transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Status */}
      <div className={`rounded-xl border ${st.border} ${st.bg} px-4 py-3 flex items-center gap-2`}>
        <div className={`w-2 h-2 rounded-full ${st.dot}`} />
        <span className={`text-sm font-semibold ${st.text}`}>{detail.health_status}</span>
        {detail.latest_severity !== null && detail.latest_severity !== undefined && (
          <span className="ml-auto text-sm text-gray-400">Severity: {detail.latest_severity.toFixed(1)}%</span>
        )}
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((alert: any, i: number) => (
            <div key={i} className={`rounded-lg border px-4 py-3 flex gap-2 items-start ${alert.severity === "critical" ? "border-red-500/30 bg-red-500/5" : alert.severity === "warning" ? "border-orange-400/30 bg-orange-400/5" : "border-blue-400/30 bg-blue-400/5"}`}>
              <AlertTriangle className={`w-4 h-4 shrink-0 mt-0.5 ${alert.severity === "critical" ? "text-red-400" : alert.severity === "warning" ? "text-orange-400" : "text-blue-400"}`} />
              <div>
                <p className="text-sm font-semibold text-gray-200">{alert.title}</p>
                <p className="text-xs text-gray-400 mt-0.5">{alert.message}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Trend Chart */}
      {trend && (
        <div className="rounded-xl border border-white/8 bg-white/3 p-4">
          <div className="flex items-center gap-2 mb-3">
            <LineChart className="w-4 h-4 text-yellow-400" />
            <h3 className="text-sm font-semibold text-gray-200">Severity Trend</h3>
          </div>
          <TrendChart trend={trend} />
        </div>
      )}

      {/* Timeline */}
      {timeline.length > 0 && (
        <div className="rounded-xl border border-white/8 bg-white/3 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold text-gray-200">Monitoring Timeline</h3>
            </div>
            <span className="text-xs text-gray-600">{timeline.length} scan{timeline.length !== 1 ? "s" : ""}</span>
          </div>
          <div className="space-y-3">
            {timeline.map((event, i) => (
              <div key={event.analysis_id} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-500/20 shrink-0 mt-1" />
                  {i < timeline.length - 1 && <div className="w-px flex-1 bg-white/8 mt-1 mb-1" />}
                </div>
                <div className={`flex-1 rounded-lg border border-white/6 bg-white/3 p-3 ${i === timeline.length - 1 ? "border-emerald-500/20" : ""}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-gray-300">{event.timeline_day}</span>
                    <span className="text-[10px] text-gray-600">{formatDate(event.timestamp)}</span>
                  </div>
                  <p className="text-xs text-gray-400 mb-1.5 truncate">{event.disease.replace(/___/g, " - ").replace(/_/g, " ")}</p>
                  <div className="flex gap-3">
                    <div>
                      <p className="text-[10px] text-gray-600">Severity</p>
                      <p className={`text-sm font-bold ${event.severity_percentage < 15 ? "text-emerald-400" : event.severity_percentage < 35 ? "text-yellow-400" : "text-red-400"}`}>
                        {event.severity_percentage.toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-600">Confidence</p>
                      <p className="text-sm font-bold text-gray-300">{(event.confidence * 100).toFixed(0)}%</p>
                    </div>
                    <div className="ml-auto flex gap-1.5">
                      <button
                        onClick={() => navigate(`/analysis/${event.analysis_id}`)}
                        className="text-[10px] text-gray-600 hover:text-gray-400 flex items-center gap-1 transition-colors"
                      >
                        <Eye className="w-3 h-3" /> View
                      </button>
                      <button
                        onClick={() => navigate(`/guidance/${event.analysis_id}`)}
                        className="text-[10px] text-emerald-500/70 hover:text-emerald-400 flex items-center gap-1 transition-colors"
                      >
                        <ArrowRight className="w-3 h-3" /> Guidance
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Scan Comparison */}
      {timeline.length >= 2 && (
        <div className="rounded-xl border border-white/8 bg-white/3 p-4">
          <div className="flex items-center gap-2 mb-3">
            <GitCompare className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-semibold text-gray-200">Compare Scans</h3>
          </div>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="text-[10px] text-gray-500 mb-1 block">Scan A</label>
              <select value={compareA} onChange={e => setCompareA(e.target.value)} className="input-field w-full text-xs">
                <option value="">— Select —</option>
                {timeline.map(t => <option key={t.analysis_id} value={t.analysis_id}>{t.timeline_day}: {t.analysis_id.slice(-6)}</option>)}
              </select>
            </div>
            <div>
              <label className="text-[10px] text-gray-500 mb-1 block">Scan B</label>
              <select value={compareB} onChange={e => setCompareB(e.target.value)} className="input-field w-full text-xs">
                <option value="">— Select —</option>
                {timeline.map(t => <option key={t.analysis_id} value={t.analysis_id}>{t.timeline_day}: {t.analysis_id.slice(-6)}</option>)}
              </select>
            </div>
          </div>
          <button
            onClick={handleCompare}
            disabled={!compareA || !compareB || compareA === compareB}
            className="w-full py-2 bg-purple-600/30 hover:bg-purple-600/50 disabled:opacity-40 text-purple-300 text-sm rounded-lg transition-colors"
          >
            Compare
          </button>
          {comparison && (
            <div className="mt-3 rounded-lg border border-purple-500/20 bg-purple-500/5 p-3 space-y-2">
              <p className="text-sm text-gray-300 font-medium">{comparison.severity_change_text}</p>
              <p className="text-xs text-gray-500">Time between scans: {comparison.time_between_scans}</p>
              <p className="text-xs text-gray-600 italic">
                This comparison shows observed visual affected-area estimates. It does not confirm treatment effectiveness.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={() => setShowLinkModal(true)}
          className="flex-1 py-2.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 text-sm font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" /> Link New Scan
        </button>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────
// Main Monitoring Page
// ─────────────────────────────────────────────────────────────────────
export default function MonitoringPage() {
  const [plants, setPlants] = useState<PlantItem[]>([])
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedPlantId, setSelectedPlantId] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [plantsResp, dashResp] = await Promise.all([
        fetch(`${API_BASE_URL}/api/plants?limit=100`),
        fetch(`${API_BASE_URL}/api/plants/dashboard`)
      ])
      if (plantsResp.ok) {
        const data = await plantsResp.json()
        setPlants(data.plants || [])
      }
      if (dashResp.ok) {
        setDashboard(await dashResp.json())
      }
    } catch {}
    setLoading(false)
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const handleDelete = async (plantId: string) => {
    if (!confirm("Remove this plant profile? Analysis records will not be deleted.")) return
    try {
      await fetch(`${API_BASE_URL}/api/plants/${plantId}`, { method: "DELETE" })
      if (selectedPlantId === plantId) setSelectedPlantId(null)
      loadData()
    } catch {}
  }

  return (
    <div className="space-y-6 pb-16">
      {showAddModal && (
        <AddPlantModal onClose={() => setShowAddModal(false)} onCreated={loadData} />
      )}

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 flex items-center justify-center">
            <Activity className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-100">Continuous Monitoring</h1>
            <p className="text-sm text-gray-500">Track plant health over time using real scan data</p>
          </div>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-xl transition-colors shadow-lg shadow-emerald-900/20"
        >
          <Plus className="w-4 h-4" /> Add Plant
        </button>
      </motion.div>

      {/* Dashboard Stats */}
      {dashboard && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Plants Monitored", value: dashboard.total_plants_monitored, icon: <Leaf className="w-4 h-4" />, color: "text-emerald-400" },
            { label: "Expert Review Needed", value: dashboard.expert_review_recommended_count, icon: <AlertTriangle className="w-4 h-4" />, color: "text-red-400" },
            { label: "Attention Recommended", value: dashboard.attention_recommended_count, icon: <AlertTriangle className="w-4 h-4" />, color: "text-orange-400" },
            { label: "Low Confidence Cases", value: dashboard.low_confidence_cases, icon: <Info className="w-4 h-4" />, color: "text-blue-400" },
          ].map((stat, i) => (
            <div key={i} className="rounded-2xl border border-white/8 bg-white/3 backdrop-blur-sm p-4">
              <div className={`${stat.color} mb-2`}>{stat.icon}</div>
              <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
              <p className="text-xs text-gray-500 mt-0.5">{stat.label}</p>
            </div>
          ))}
        </motion.div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <div className="w-10 h-10 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
        </div>
      )}

      {/* Empty state */}
      {!loading && plants.length === 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          className="rounded-2xl border border-white/8 bg-white/3 p-12 text-center"
        >
          <Leaf className="w-12 h-12 text-gray-700 mx-auto mb-4" />
          <p className="text-lg font-semibold text-gray-400 mb-2">No plants monitored yet</p>
          <p className="text-sm text-gray-600 mb-6 max-w-sm mx-auto">
            Add a plant profile to start tracking health over time. Link analyses to build a monitoring timeline.
          </p>
          <button onClick={() => setShowAddModal(true)}
            className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-xl transition-colors">
            Add First Plant
          </button>
        </motion.div>
      )}

      {/* Plant Grid + Detail Panel */}
      {!loading && plants.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Plant Cards */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-gray-400">
                {plants.length} Plant{plants.length !== 1 ? "s" : ""}
              </h2>
              <button onClick={loadData} className="text-gray-600 hover:text-gray-400 transition-colors">
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <AnimatePresence>
                {plants.map(plant => (
                  <PlantCard
                    key={plant.plant_id}
                    plant={plant}
                    onDelete={handleDelete}
                    onSelect={id => setSelectedPlantId(id === selectedPlantId ? null : id)}
                    selected={selectedPlantId === plant.plant_id}
                  />
                ))}
              </AnimatePresence>
            </div>
          </div>

          {/* Detail Panel */}
          <div>
            {selectedPlantId ? (
              <div className="rounded-2xl border border-white/10 bg-white/3 backdrop-blur-sm p-5 sticky top-4">
                <PlantDetailPanel
                  key={selectedPlantId}
                  plantId={selectedPlantId}
                  onClose={() => setSelectedPlantId(null)}
                  onRefresh={loadData}
                />
              </div>
            ) : (
              <div className="rounded-2xl border border-white/6 bg-white/2 p-8 text-center sticky top-4">
                <Eye className="w-8 h-8 text-gray-700 mx-auto mb-3" />
                <p className="text-sm text-gray-600">Select a plant to view its timeline, trend, and alerts</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="rounded-xl border border-white/6 bg-white/2 p-4 mt-4">
        <p className="text-[11px] text-gray-600 leading-relaxed">
          <strong className="text-gray-500">Monitoring Note:</strong> All timeline records are based on real stored analyses only.
          No synthetic or fabricated scan data is generated. Severity trends represent observed visual affected-area estimates
          and do not imply causal proof or treatment effectiveness.
        </p>
      </div>
    </div>
  )
}
