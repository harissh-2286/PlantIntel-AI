import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { getSingleAnalysis, SingleAnalysisResponse, deleteAnalysis } from "@/services/api"
import { 
  ArrowLeft, 
  Download, 
  FileText, 
  Trash2, 
  Cpu, 
  Activity, 
  Layers, 
  Info, 
  AlertTriangle, 
  Calendar
} from "lucide-react"

export default function AnalysisDetail() {
  const { analysis_id } = useParams<{ analysis_id: string }>()
  const navigate = useNavigate()
  
  const [data, setData] = useState<SingleAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showPreviewModal, setShowPreviewModal] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [activeTab, setActiveTab] = useState<'gradcam' | 'severity' | 'original'>('gradcam')

  useEffect(() => {
    if (!analysis_id) return
    const fetchRecord = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await getSingleAnalysis(analysis_id)
        setData(res)
      } catch (err: any) {
        setError(err.message || "Failed to load analysis record.")
      } finally {
        setLoading(false)
      }
    }
    fetchRecord()
  }, [analysis_id])

  const handleDelete = async () => {
    if (!analysis_id || deleting) return
    if (!window.confirm(`Are you sure you want to delete analysis record ${analysis_id}? This action cannot be undone.`)) return
    
    setDeleting(true)
    try {
      await deleteAnalysis(analysis_id)
      navigate('/history')
    } catch (err: any) {
      alert(err.message || "Failed to delete analysis.")
      setDeleting(false)
    }
  }

  const cleanClassName = (raw: string) => {
    if (!raw) return ""
    return raw.replace('ImageNet class: ', '').replace(/___/g, ' - ').replace(/_/g, ' ')
  }

  if (loading) {
    return (
      <div className="h-[65vh] flex flex-col items-center justify-center text-center p-8">
        <div className="w-12 h-12 rounded-full border-4 border-primary/30 border-t-primary animate-spin mb-4"></div>
        <h3 className="font-semibold text-lg text-foreground">Loading Analysis Record...</h3>
        <p className="text-xs text-muted-foreground mt-1 font-mono">{analysis_id}</p>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="h-[65vh] flex flex-col items-center justify-center text-center p-8 space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-destructive/10 flex items-center justify-center text-destructive border border-destructive/20">
          <AlertTriangle className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-foreground">Report Unavailable</h2>
        <p className="text-sm text-muted-foreground max-w-md">{error || "The requested analysis record does not exist or has been deleted."}</p>
        <Button onClick={() => navigate('/history')} className="mt-2 bg-primary text-primary-foreground font-semibold">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to History
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-8 pb-12">
      {/* NAVIGATION & ACTION BAR */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={() => navigate('/history')} className="text-xs border-white/10">
            <ArrowLeft className="w-4 h-4 mr-1.5" /> Back to History
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-lg font-bold text-primary">{data.analysis_id}</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase">
                {data.analysis_status}
              </span>
            </div>
            <p className="text-xs text-muted-foreground flex items-center gap-2 mt-0.5 font-mono">
              <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
              {data.created_at ? new Date(data.created_at).toLocaleString() : 'N/A'}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => window.open(`/api/report/${encodeURIComponent(data.analysis_id)}/pdf`, '_blank')} 
            className="text-xs border-primary/30 text-primary hover:bg-primary/10"
          >
            <Download className="w-3.5 h-3.5 mr-1.5" /> Download PDF Report
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => window.open(`/api/report/${encodeURIComponent(data.analysis_id)}/json`, '_blank')} 
            className="text-xs border-white/10"
          >
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export JSON
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setShowPreviewModal(true)} 
            className="text-xs border-white/10"
          >
            <FileText className="w-3.5 h-3.5 mr-1.5" /> Report Preview
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => navigate(`/guidance/${encodeURIComponent(data.analysis_id)}`)} 
            className="text-xs border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"
          >
            🌱 Plant Health Guidance
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleDelete} 
            disabled={deleting} 
            className="text-xs border-destructive/30 text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="w-3.5 h-3.5 mr-1.5" /> {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </div>

      {/* TOP SUMMARY CARDS */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* CARD 1: PREDICTED DISEASE */}
        <Card className="border-t-4 border-t-primary bg-card/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-primary" /> Disease Prediction
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-1 space-y-3">
            <h2 className="text-2xl font-extrabold capitalize text-foreground leading-tight">
              {cleanClassName(data.prediction.class_name)}
            </h2>
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground">Model confidence</span>
                <span className="font-bold text-primary font-mono">{(data.prediction.confidence * 100).toFixed(2)}%</span>
              </div>
              <Progress value={data.prediction.confidence * 100} className="h-2 bg-white/10" />
            </div>
            <p className="text-[11px] text-muted-foreground font-mono">
              Model: <strong className="text-foreground">{data.model.name}</strong> ({data.model.mode || 'attention'})
            </p>
          </CardContent>
        </Card>

        {/* CARD 2: SEVERITY ANALYSIS */}
        <Card className="border-t-4 border-t-emerald-400 bg-card/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-muted-foreground flex items-center justify-between">
              <span className="flex items-center gap-1.5"><Activity className="w-4 h-4 text-emerald-400" /> Severity Analysis</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px] uppercase">
                {data.severity.level}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-1 space-y-3">
            <div className="text-3xl font-black text-emerald-400">
              {data.severity.percentage.toFixed(2)}%
            </div>
            <p className="text-xs font-semibold text-muted-foreground">Estimated Affected Leaf Area</p>
            <div className="grid grid-cols-2 gap-2 text-[11px] bg-white/5 p-2.5 rounded-lg font-mono">
              <div>
                <span className="text-muted-foreground block font-sans">Leaf Area</span>
                <strong className="text-foreground">{data.area.leaf_pixels.toLocaleString()} px</strong>
              </div>
              <div>
                <span className="text-muted-foreground block font-sans">Affected Area</span>
                <strong className="text-emerald-400">{data.area.affected_pixels.toLocaleString()} px</strong>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* CARD 3: IMAGE METADATA */}
        <Card className="border-t-4 border-t-cyan-400 bg-card/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-cyan-400" /> Image Metadata
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-1 space-y-3 text-xs">
            <div className="p-2.5 bg-white/5 rounded-lg space-y-1 font-mono">
              <span className="text-muted-foreground block font-sans">Stored Filename</span>
              <span className="font-semibold text-foreground truncate block" title={data.image_filename}>
                {data.image_filename}
              </span>
            </div>
            <div className="p-2.5 bg-white/5 rounded-lg space-y-1 font-mono">
              <span className="text-muted-foreground block font-sans">Dimensions</span>
              <span className="font-semibold text-foreground">
                {data.image_width && data.image_height ? `${data.image_width} × ${data.image_height} px` : '224 × 224 px'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* VISUALIZATION WORKBENCH */}
      <Card className="border-white/10">
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-base font-semibold">Saved Visual Artifacts</CardTitle>
          <div className="flex bg-black/40 p-1 rounded-lg border border-white/10 gap-1 text-xs">
            <button
              onClick={() => setActiveTab('gradcam')}
              className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'gradcam' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground'}`}
            >
              Grad-CAM++ Overlay
            </button>
            <button
              onClick={() => setActiveTab('severity')}
              className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'severity' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground'}`}
            >
              Severity Mask
            </button>
            <button
              onClick={() => setActiveTab('original')}
              className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'original' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground'}`}
            >
              Original Upload
            </button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="aspect-video rounded-xl bg-black/60 border border-white/10 overflow-hidden flex items-center justify-center p-2">
            {activeTab === 'gradcam' && data.visualizations?.gradcam_overlay ? (
              <img src={data.visualizations.gradcam_overlay} alt="Grad-CAM++ overlay" className="max-w-full max-h-full object-contain rounded-lg" />
            ) : activeTab === 'severity' && data.visualizations?.severity_overlay ? (
              <img src={data.visualizations.severity_overlay} alt="Severity overlay" className="max-w-full max-h-full object-contain rounded-lg" />
            ) : data.image_url ? (
              <img src={data.image_url} alt="Original upload" className="max-w-full max-h-full object-contain rounded-lg" />
            ) : (
              <div className="p-4 text-xs text-muted-foreground">Explanation visualization unavailable.</div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* TOP PREDICTIONS TABLE */}
      {data.top_predictions && data.top_predictions.length > 0 && (
        <Card className="border-white/10">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold">Top Classification Candidates</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.top_predictions.slice(0, 5).map((pred, i) => (
              <div key={pred.class_id} className="flex items-center gap-4 text-xs">
                <span className="w-6 font-mono text-muted-foreground font-semibold text-center">#{i + 1}</span>
                <span className="w-48 sm:w-64 truncate font-medium capitalize text-foreground">
                  {cleanClassName(pred.class_name)}
                </span>
                <div className="flex-1">
                  <Progress value={pred.confidence * 100} className={`h-2 ${i === 0 ? 'bg-primary/20' : 'bg-white/5'}`} />
                </div>
                <span className="w-16 text-right font-mono font-bold text-foreground">
                  {(pred.confidence * 100).toFixed(2)}%
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* SCIENTIFIC DISCLAIMER BANNER */}
      <div className="p-4 bg-white/5 border border-white/5 rounded-xl text-xs text-muted-foreground flex items-start gap-3">
        <Info className="w-4 h-4 text-muted-foreground flex-shrink-0 mt-0.5" />
        <div>
          <strong className="text-foreground">Mandatory Scientific Disclaimer:</strong> AI-assisted analysis only. Results depend on image quality, training data, model performance, and the severity-estimation method. The explanation visualizations indicate model-associated image regions and should not be interpreted as ground-truth disease segmentation.
        </div>
      </div>

      {/* REPORT PREVIEW MODAL */}
      {showPreviewModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border border-white/10 rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 space-y-6 text-foreground">
            <div className="flex justify-between items-center border-b border-white/10 pb-4">
              <div>
                <span className="text-[10px] font-mono uppercase text-primary tracking-wider">Report Preview</span>
                <h3 className="text-xl font-bold">PlantIntel AI — Prediction Report</h3>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setShowPreviewModal(false)}>Close</Button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-4 bg-white/5 rounded-xl space-y-2 font-mono">
                <p><strong>Analysis ID:</strong> {data.analysis_id}</p>
                <p><strong>Date Generated:</strong> {data.created_at ? new Date(data.created_at).toLocaleString() : 'N/A'}</p>
                <p><strong>Predicted Disease:</strong> {cleanClassName(data.prediction.class_name)}</p>
                <p><strong>Confidence:</strong> {(data.prediction.confidence * 100).toFixed(2)}%</p>
                <p><strong>Severity Category:</strong> {data.severity.level} ({data.severity.percentage.toFixed(2)}% affected area)</p>
                <p><strong>Model:</strong> {data.model.name} ({data.model.mode || 'attention'})</p>
              </div>

              <div className="p-4 bg-white/5 border border-white/10 rounded-xl space-y-2 text-muted-foreground italic">
                <p className="font-semibold text-foreground not-italic">Disclaimer Notice:</p>
                <p>AI-assisted analysis only. Results depend on image quality, training data, model performance, and the severity-estimation method. The explanation visualizations indicate model-associated image regions and should not be interpreted as ground-truth disease segmentation.</p>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
              <Button variant="outline" size="sm" onClick={() => setShowPreviewModal(false)}>Cancel</Button>
              <Button 
                size="sm" 
                onClick={() => {
                  setShowPreviewModal(false)
                  window.open(`/api/report/${encodeURIComponent(data.analysis_id)}/pdf`, '_blank')
                }}
                className="bg-primary text-primary-foreground font-semibold"
              >
                <Download className="w-3.5 h-3.5 mr-1.5" /> Download Full PDF
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
