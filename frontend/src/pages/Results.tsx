import { useState, useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { UploadCloud, Sparkles, Cpu, Activity, FileText, Download, CheckCircle2, Layers, Info } from "lucide-react"
import { AnalyzeFullResponse } from "@/services/api"

export default function Results() {
  const location = useLocation()
  const navigate = useNavigate()
  const [data, setData] = useState<AnalyzeFullResponse | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [severityTab, setSeverityTab] = useState<'overlay' | 'affected' | 'original'>('overlay')

  useEffect(() => {
    if (location.state?.analysisResult) {
      setData(location.state.analysisResult)
    }
    if (location.state?.file) {
      setFile(location.state.file)
    }
  }, [location.state])

  const cleanClassName = (raw: string) => {
    if (!raw) return ""
    return raw.replace('ImageNet class: ', '').replace(/___/g, ' - ').replace(/_/g, ' ')
  }

  const exportJSON = () => {
    if (!data) return
    const jsonStr = JSON.stringify(data, null, 2)
    const blob = new Blob([jsonStr], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `PlantIntel_Analysis_${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const exportCSV = () => {
    if (!data) return
    const csvContent = [
      ["Metric", "Value"],
      ["Predicted Disease", cleanClassName(data.prediction.class_name)],
      ["Model Confidence", `${(data.prediction.confidence * 100).toFixed(2)}%`],
      ["Model Architecture", data.model.architecture],
      ["Affected Leaf Area %", `${data.severity.percentage.toFixed(2)}%`],
      ["Severity Level", data.severity.level],
      ["Leaf Pixels", data.area.leaf_pixels],
      ["Affected Pixels", data.area.affected_pixels],
      ["Inference Latency", `${data.inference_time_ms} ms`]
    ].map(e => e.join(",")).join("\n")

    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `PlantIntel_Analysis_${Date.now()}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const printReport = () => {
    window.print()
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-[65vh] text-center space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
          <UploadCloud className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight">Analysis Results</h1>
        <p className="text-muted-foreground max-w-md">
          Upload and run leaf classification from the Analyze workbench to view complete disease classification, severity estimation, and model predictions.
        </p>
        <div className="flex gap-3 mt-4">
          <Button onClick={() => navigate('/analyze')} className="bg-primary text-primary-foreground font-semibold">
            Go to Analyze Workbench
          </Button>
          <Button variant="secondary" onClick={() => navigate('/explainability')}>
            <Sparkles className="w-4 h-4 mr-2" /> Explainability
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 pb-12">
      {/* HEADER SECTION */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <CheckCircle2 className="w-3.5 h-3.5" /> Analysis Complete
          </div>
          <h1 className="text-3xl font-black tracking-tight">Leaf Intelligence Prediction Report</h1>
          <p className="text-xs text-muted-foreground mt-1 font-mono">
            Analysis ID: PI-{Date.now().toString().slice(-8)} • Timestamp: {new Date().toLocaleString()}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button variant="outline" size="sm" onClick={exportCSV} className="text-xs border-white/10">
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export CSV
          </Button>
          <Button variant="outline" size="sm" onClick={exportJSON} className="text-xs border-white/10">
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export JSON
          </Button>
          <Button size="sm" onClick={printReport} className="text-xs bg-primary text-primary-foreground font-semibold">
            <FileText className="w-3.5 h-3.5 mr-1.5" /> Print Report
          </Button>
        </div>
      </div>

      {/* TOP METRICS SUMMARY GRID */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* CARD 1: PREDICTED DISEASE */}
        <Card className="border-t-4 border-t-primary bg-card/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-primary" /> Predicted Disease
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
            <p className="text-[11px] text-muted-foreground">
              Architecture: <strong className="text-foreground">{data.model.architecture}</strong>
            </p>
          </CardContent>
        </Card>

        {/* CARD 2: SEVERITY ESTIMATION */}
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
                <span className="text-muted-foreground block">Leaf Area</span>
                <strong className="text-foreground">{data.area.leaf_pixels.toLocaleString()} px</strong>
              </div>
              <div>
                <span className="text-muted-foreground block">Affected Area</span>
                <strong className="text-emerald-400">{data.area.affected_pixels.toLocaleString()} px</strong>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* CARD 3: MODEL COMPOSITION */}
        <Card className="border-t-4 border-t-cyan-400 bg-card/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-cyan-400" /> Model Pipeline
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-1 space-y-3 text-xs">
            <div className="p-2.5 bg-white/5 rounded-lg space-y-1">
              <span className="text-muted-foreground block">Backbone Model</span>
              <span className="font-bold text-foreground">EfficientNetV2-S</span>
            </div>
            <div className="p-2.5 bg-white/5 rounded-lg space-y-1">
              <span className="text-muted-foreground block">Proposed Attention</span>
              <span className="font-bold text-primary">Adaptive Lightweight Attention</span>
            </div>
            <div className="flex justify-between items-center text-[11px] text-muted-foreground pt-1">
              <span>Inference Time:</span>
              <span className="font-mono text-foreground font-semibold">{data.inference_time_ms} ms</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* TOP 5 PREDICTIONS BREAKDOWN */}
      <Card className="border-white/10">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold">Top 5 Classification Candidates</CardTitle>
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

      {/* SEVERITY VISUALIZATION WORKBENCH */}
      <Card className="border-white/10">
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-base font-semibold">Estimated Affected Region Visualization</CardTitle>
          <div className="flex bg-black/40 p-1 rounded-lg border border-white/10 gap-1 text-xs">
            <button
              onClick={() => setSeverityTab('overlay')}
              className={`px-3 py-1 rounded-md transition-colors ${severityTab === 'overlay' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground'}`}
            >
              Overlay
            </button>
            <button
              onClick={() => setSeverityTab('affected')}
              className={`px-3 py-1 rounded-md transition-colors ${severityTab === 'affected' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground'}`}
            >
              Affected Region
            </button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="aspect-video rounded-xl bg-black/60 border border-white/10 overflow-hidden flex items-center justify-center p-2">
            {data.severity_visualization ? (
              <img src={data.severity_visualization} alt="Severity mask overlay" className="max-w-full max-h-full object-contain rounded-lg" />
            ) : (
              <div className="p-4 text-xs text-muted-foreground">Visualization not generated.</div>
            )}
          </div>
          <p className="text-xs text-muted-foreground text-center">
            Highlighted red regions indicate isolated candidate disease regions (chlorosis, necrosis, and spots) inside the detected leaf boundary.
          </p>
        </CardContent>
      </Card>

      {/* EXPLAINABILITY ACTION BANNER */}
      <Card className="border-primary/30 bg-primary/10">
        <CardContent className="p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-center sm:text-left">
            <h3 className="text-lg font-bold text-foreground flex items-center gap-2 justify-center sm:justify-start">
              <Sparkles className="w-5 h-5 text-primary" /> Why did the model make this prediction?
            </h3>
            <p className="text-xs text-muted-foreground">
              Generate 2nd-order Grad-CAM++ class activation maps and inspect feature contribution heatmaps.
            </p>
          </div>
          <Button 
            onClick={() => navigate('/explainability', { state: { file } })}
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold shadow-lg"
          >
            Explain This Prediction (Grad-CAM++)
          </Button>
        </CardContent>
      </Card>

      {/* LEGAL & SCIENTIFIC LIMITATION DISCLAIMER */}
      <div className="p-4 bg-white/5 border border-white/5 rounded-xl text-xs text-muted-foreground flex items-start gap-3">
        <Info className="w-4 h-4 text-muted-foreground flex-shrink-0 mt-0.5" />
        <div>
          <strong className="text-foreground">Important Scientific Limitation:</strong> AI-assisted analysis; results depend on image quality and model performance. Affected area estimation and Grad-CAM++ feature maps are visual aids and should not replace professional agricultural diagnostic verification.
        </div>
      </div>
    </div>
  )
}
