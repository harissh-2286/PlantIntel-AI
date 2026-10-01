import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { 
  getHistory, 
  deleteAnalysis, 
  HistoryResponse 
} from "@/services/api"
import { 
  Search, 
  History as HistoryIcon, 
  FileImage, 
  Download, 
  Trash2, 
  Eye, 
  ChevronLeft, 
  ChevronRight
} from "lucide-react"

export default function History() {
  const navigate = useNavigate()
  
  const [data, setData] = useState<HistoryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Query State
  const [search, setSearch] = useState("")
  const [severityFilter, setSeverityFilter] = useState("")
  const [sortBy, setSortBy] = useState("newest")
  const [offset, setOffset] = useState(0)
  const limit = 20

  const fetchHistoryData = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getHistory({
        limit,
        offset,
        search: search.trim() || undefined,
        severity: severityFilter || undefined,
        sort_by: sortBy
      })
      setData(res)
    } catch (err: any) {
      setError(err.message || "Failed to load analysis history.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistoryData()
  }, [offset, severityFilter, sortBy])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setOffset(0)
    fetchHistoryData()
  }

  const handleDelete = async (analysisId: string) => {
    if (!window.confirm(`Delete analysis record ${analysisId}? This will remove stored image and visualization artifacts.`)) return
    try {
      await deleteAnalysis(analysisId)
      fetchHistoryData()
    } catch (err: any) {
      alert(err.message || "Failed to delete record.")
    }
  }

  const cleanClassName = (raw: string) => {
    if (!raw) return ""
    return raw.replace('ImageNet class: ', '').replace(/___/g, ' - ').replace(/_/g, ' ')
  }

  return (
    <div className="space-y-8 pb-12">
      {/* HEADER SECTION */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/20 text-primary text-xs font-semibold uppercase tracking-wider mb-2">
            <HistoryIcon className="w-3.5 h-3.5" /> Persistent Database Log
          </div>
          <h1 className="text-3xl font-black tracking-tight">Analysis History</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Search, filter, inspect, and export persistent deep learning analysis records stored in SQLite database.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => window.open('/api/history/export/csv', '_blank')}
            className="text-xs border-white/10"
          >
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export History CSV
          </Button>
          <Button size="sm" onClick={() => navigate('/analyze')} className="text-xs bg-primary text-primary-foreground font-semibold">
            + New Analysis
          </Button>
        </div>
      </div>

      {/* FILTER & SEARCH CONTROL BAR */}
      <Card className="bg-card/60 border-white/10">
        <CardContent className="p-4 flex flex-col md:flex-row gap-4 items-center justify-between">
          {/* Search Input */}
          <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search ID or disease name..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-xs text-foreground focus:outline-none focus:border-primary/50"
            />
          </form>

          {/* Filters & Sorting */}
          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            {/* Severity Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground font-medium">Severity:</span>
              <select 
                value={severityFilter}
                onChange={(e) => { setSeverityFilter(e.target.value); setOffset(0); }}
                className="bg-black/40 border border-white/10 text-xs rounded-lg px-3 py-2 text-foreground focus:outline-none"
              >
                <option value="">All Severities</option>
                <option value="Minimal">Minimal</option>
                <option value="Mild">Mild</option>
                <option value="Moderate">Moderate</option>
                <option value="Severe">Severe</option>
                <option value="Very Severe">Very Severe</option>
              </select>
            </div>

            {/* Sort Order */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground font-medium">Sort:</span>
              <select 
                value={sortBy}
                onChange={(e) => { setSortBy(e.target.value); setOffset(0); }}
                className="bg-black/40 border border-white/10 text-xs rounded-lg px-3 py-2 text-foreground focus:outline-none"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="confidence">Highest Confidence</option>
                <option value="severity">Highest Severity</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* TABLE DATA */}
      <Card className="border-white/10">
        <CardContent className="p-0 overflow-x-auto">
          {loading ? (
            <div className="py-20 text-center text-xs text-muted-foreground">
              <div className="w-8 h-8 rounded-full border-2 border-primary/30 border-t-primary animate-spin mx-auto mb-3"></div>
              Loading analysis history records...
            </div>
          ) : error ? (
            <div className="py-12 text-center text-xs text-destructive">{error}</div>
          ) : !data || data.items.length === 0 ? (
            <div className="py-20 text-center text-muted-foreground">
              <FileImage className="w-12 h-12 mx-auto mb-3 text-muted-foreground opacity-30" />
              <p className="text-base font-semibold text-foreground">No analyses yet.</p>
              <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
                Upload a leaf image to begin disease classification, severity estimation, and Grad-CAM++ explanations.
              </p>
              <Button size="sm" onClick={() => navigate('/analyze')} className="mt-4 bg-primary text-primary-foreground font-semibold">
                Go to Analyze Workbench
              </Button>
            </div>
          ) : (
            <table className="w-full text-sm text-left">
              <thead className="text-xs font-mono uppercase bg-white/5 text-muted-foreground border-b border-white/10">
                <tr>
                  <th className="px-6 py-4">Analysis ID</th>
                  <th className="px-6 py-4">Timestamp</th>
                  <th className="px-6 py-4">Predicted Disease</th>
                  <th className="px-6 py-4">Confidence</th>
                  <th className="px-6 py-4">Severity Level</th>
                  <th className="px-6 py-4">Affected Area</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-mono text-xs">
                {data.items.map((item) => (
                  <tr key={item.analysis_id} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4 font-bold text-primary">
                      {item.analysis_id}
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 font-sans font-medium text-foreground capitalize">
                      {cleanClassName(item.predicted_class)}
                    </td>
                    <td className="px-6 py-4 font-bold text-foreground">
                      {(item.confidence * 100).toFixed(2)}%
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-semibold text-[10px] uppercase">
                        {item.severity_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-foreground font-semibold">
                      {item.severity_percentage.toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => navigate(`/analysis/${encodeURIComponent(item.analysis_id)}`)}
                          className="h-8 text-xs text-primary hover:text-primary hover:bg-primary/10"
                        >
                          <Eye className="w-3.5 h-3.5 mr-1" /> View
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => handleDelete(item.analysis_id)}
                          className="h-8 text-xs text-destructive hover:text-destructive hover:bg-destructive/10"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      {/* PAGINATION BAR */}
      {data && data.total > 0 && (
        <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
          <div>
            Showing {offset + 1}–{Math.min(offset + limit, data.total)} of {data.total} records
          </div>
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              disabled={offset === 0 || loading} 
              onClick={() => setOffset(Math.max(0, offset - limit))}
              className="text-xs border-white/10"
            >
              <ChevronLeft className="w-3.5 h-3.5 mr-1" /> Previous
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              disabled={offset + limit >= data.total || loading} 
              onClick={() => setOffset(offset + limit)}
              className="text-xs border-white/10"
            >
              Next <ChevronRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
