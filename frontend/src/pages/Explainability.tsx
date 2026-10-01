import { useState, useEffect } from "react"
import { useLocation } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { UploadCloud, AlertTriangle, Eye, Layers, Info, Sparkles } from "lucide-react"
import { getCombinedExplanation, CombinedExplainResponse, getGradCAMExplanation } from "@/services/api"

export default function Explainability() {
  const location = useLocation()
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState<string>("Preparing model explanation...")
  const [result, setResult] = useState<CombinedExplainResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overlay' | 'original' | 'heatmap' | 'side_by_side'>('side_by_side')
  const [selectedTargetClass, setSelectedTargetClass] = useState<number | null>(null)

  // Handle incoming file from location state (e.g. from Analyze page "Explain This Prediction" button)
  useEffect(() => {
    if (location.state?.file) {
      handleFileChange(location.state.file)
    }
  }, [location.state])

  const handleFileChange = (f: File) => {
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    setError(null)
    setSelectedTargetClass(null)
    runExplanation(f, undefined)
  }

  const runExplanation = async (targetFile: File | null = file, targetClassId?: number) => {
    if (!targetFile) return
    setLoading(true)
    setError(null)

    try {
      setLoadingStep("Preparing model explanation...")
      await new Promise((r) => setTimeout(r, 200))
      
      setLoadingStep("Generating Grad-CAM++...")
      await new Promise((r) => setTimeout(r, 200))

      setLoadingStep("Rendering heatmap...")
      const res = await getCombinedExplanation(targetFile, targetClassId)
      
      setResult(res)
      if (res.prediction && selectedTargetClass === null) {
        setSelectedTargetClass(res.prediction.class_id)
      }
      setLoadingStep("Explanation ready.")
    } catch (err: any) {
      setError(err.message || "Unable to generate an explanation for this image.")
    } finally {
      setLoading(false)
    }
  }

  const handleTargetClassSelect = async (classId: number) => {
    if (!file || loading) return
    setSelectedTargetClass(classId)
    setLoading(true)
    setError(null)
    setLoadingStep(`Generating Grad-CAM++ for Target Class #${classId}...`)

    try {
      const gradcamRes = await getGradCAMExplanation(file, classId)
      if (result) {
        setResult({
          ...result,
          prediction: gradcamRes.prediction,
          gradcam: gradcamRes.explanation,
          explanation_time_ms: gradcamRes.explanation_time_ms
        })
      }
      setLoadingStep("Explanation ready.")
    } catch (err: any) {
      setError(err.message || "Failed to update explanation for target class.")
    } finally {
      setLoading(false)
    }
  }

  const cleanClassName = (raw: string) => {
    if (!raw) return ""
    return raw.replace('ImageNet class: ', '').replace(/___/g, ' - ').replace(/_/g, ' ')
  }

  return (
    <div className="space-y-8">
      {/* Title & Introduction */}
      <div>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Why did the model make this prediction?</h1>
            <p className="text-muted-foreground mt-1">
              Gradient-weighted Class Activation Mapping (Grad-CAM++) post-hoc visual explanation & internal Adaptive Attention analysis.
            </p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column: Image Selector & Controls */}
        <div className="space-y-6">
          <Card className="border-white/10 bg-card/60 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <UploadCloud className="w-4 h-4 text-primary" /> Leaf Image Input
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!preview ? (
                <label className="border-2 border-dashed border-white/10 rounded-xl p-8 text-center flex flex-col items-center justify-center cursor-pointer hover:bg-white/5 transition-colors group">
                  <input 
                    type="file" 
                    className="hidden" 
                    accept="image/jpeg, image/png, image/jpg"
                    onChange={(e) => e.target.files && e.target.files[0] && handleFileChange(e.target.files[0])}
                  />
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary mb-3 group-hover:scale-110 transition-transform">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <span className="text-sm font-medium">Click or drag leaf image</span>
                  <span className="text-xs text-muted-foreground mt-1">JPG, PNG up to 10MB</span>
                </label>
              ) : (
                <div className="space-y-4">
                  <div className="relative aspect-square rounded-xl overflow-hidden bg-black/60 border border-white/10 flex items-center justify-center">
                    <img src={preview} alt="Input leaf" className="max-w-full max-h-full object-contain" />
                  </div>
                  <div className="flex gap-2">
                    <label className="flex-1">
                      <input 
                        type="file" 
                        className="hidden" 
                        accept="image/jpeg, image/png, image/jpg"
                        onChange={(e) => e.target.files && e.target.files[0] && handleFileChange(e.target.files[0])}
                      />
                      <Button variant="secondary" className="w-full text-xs" disabled={loading}>Change Image</Button>
                    </label>
                    <Button 
                      onClick={() => file && runExplanation(file, selectedTargetClass ?? undefined)} 
                      disabled={loading || !file} 
                      className="flex-1 text-xs"
                    >
                      {loading ? 'Processing...' : 'Re-Explain'}
                    </Button>
                  </div>
                </div>
              )}

              {error && (
                <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-xs text-destructive flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Target Class Exploration Menu */}
          {result && result.top_predictions && result.top_predictions.length > 0 && (
            <Card className="border-white/10 bg-card/60">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold flex items-center justify-between">
                  <span>Target Class Exploration</span>
                  <span className="text-[10px] text-muted-foreground font-normal">Advanced Selection</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-xs text-muted-foreground">
                  Select a class below to compute Grad-CAM++ feature contributions specifically for that disease hypothesis:
                </p>

                <div className="space-y-2">
                  {result.top_predictions.slice(0, 3).map((pred, idx) => {
                    const isSelected = selectedTargetClass === pred.class_id
                    return (
                      <button
                        key={pred.class_id}
                        onClick={() => handleTargetClassSelect(pred.class_id)}
                        disabled={loading}
                        className={`w-full text-left p-2.5 rounded-lg border text-xs transition-all flex items-center justify-between ${
                          isSelected 
                            ? 'bg-primary/15 border-primary text-primary font-semibold shadow-[0_0_10px_rgba(20,180,100,0.15)]' 
                            : 'bg-white/5 border-white/5 hover:bg-white/10 text-muted-foreground'
                        }`}
                      >
                        <div className="truncate pr-2">
                          <span className="text-[10px] font-mono uppercase block text-muted-foreground">
                            {idx === 0 ? 'Predicted (Top-1)' : `Top-${idx + 1} Candidate`}
                          </span>
                          <span className="truncate block font-medium capitalize text-foreground">
                            {cleanClassName(pred.class_name)}
                          </span>
                        </div>
                        <span className="font-mono text-xs text-primary bg-black/40 px-2 py-1 rounded">
                          {(pred.confidence * 100).toFixed(1)}%
                        </span>
                      </button>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Scientific Limitations Card */}
          <Card className="border-white/10 bg-card/40">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5 uppercase tracking-wider">
                <Info className="w-4 h-4 text-primary" /> About This Explanation
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-2">
              <p className="text-xs text-muted-foreground leading-relaxed">
                Grad-CAM++ is an explanation technique that highlights image regions contributing to a selected model prediction. It should not be interpreted as a ground-truth disease segmentation or as proof of causal reasoning.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Visualization & Comparison Workbench */}
        <div className="lg:col-span-2 space-y-6">
          {loading && (
            <Card className="h-96 flex flex-col items-center justify-center text-center p-8 border-white/10">
              <div className="w-12 h-12 rounded-full border-4 border-primary/30 border-t-primary animate-spin mb-4"></div>
              <h3 className="font-semibold text-lg">{loadingStep}</h3>
              <p className="text-xs text-muted-foreground mt-2 max-w-xs">
                Computing feature map activations & backward gradients for EfficientNetV2-S.
              </p>
            </Card>
          )}

          {!loading && !result && (
            <Card className="h-96 flex flex-col items-center justify-center text-center p-8 border-dashed border-white/10">
              <Eye className="w-12 h-12 text-muted-foreground mb-4 opacity-50" />
              <h3 className="font-medium text-lg">No Explanation Rendered</h3>
              <p className="text-xs text-muted-foreground max-w-sm mt-1">
                Upload a leaf image to generate live Grad-CAM++ heatmaps and compare against Adaptive Attention maps.
              </p>
            </Card>
          )}

          {!loading && result && (
            <div className="space-y-6">
              {/* Prediction Summary Header Card */}
              <Card className="border-primary/20 bg-primary/5">
                <CardContent className="p-4 flex flex-wrap items-center justify-between gap-4">
                  <div className="space-y-1">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                      Model Prediction Summary
                    </span>
                    <h2 className="text-xl font-bold capitalize text-foreground">
                      {cleanClassName(result.prediction.class_name)}
                    </h2>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span>Explanation Target: <strong className="text-primary">{cleanClassName(result.prediction.class_name)}</strong></span>
                      <span>•</span>
                      <span>Target Layer: <strong className="font-mono text-foreground">{result.gradcam.target_layer}</strong></span>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <span className="text-[10px] text-muted-foreground uppercase block">Confidence</span>
                      <span className="text-xl font-bold text-primary">{(result.prediction.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="text-right border-l border-white/10 pl-6">
                      <span className="text-[10px] text-muted-foreground uppercase block">Explanation Method</span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-primary/20 text-primary border border-primary/30 inline-block mt-0.5">
                        {result.gradcam.method}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Main Image Viewer Workbench */}
              <Card className="border-white/10">
                <CardHeader className="pb-3 flex flex-row items-center justify-between">
                  <CardTitle className="text-base font-semibold">Grad-CAM++ Visual Comparison</CardTitle>
                  <div className="flex bg-black/40 p-1 rounded-lg border border-white/10 gap-1 text-xs">
                    <button
                      onClick={() => setActiveTab('side_by_side')}
                      className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'side_by_side' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}
                    >
                      Side-by-Side
                    </button>
                    <button
                      onClick={() => setActiveTab('overlay')}
                      className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'overlay' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}
                    >
                      Overlay
                    </button>
                    <button
                      onClick={() => setActiveTab('heatmap')}
                      className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'heatmap' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}
                    >
                      Heatmap
                    </button>
                    <button
                      onClick={() => setActiveTab('original')}
                      className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'original' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}
                    >
                      Original
                    </button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* View Modes */}
                  {activeTab === 'side_by_side' ? (
                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="space-y-2 text-center">
                        <p className="text-xs font-semibold text-muted-foreground">Original Leaf</p>
                        <div className="aspect-square rounded-xl bg-black/50 border border-white/10 overflow-hidden flex items-center justify-center p-1">
                          <img src={result.gradcam.original} alt="Original" className="max-w-full max-h-full object-contain rounded-lg" />
                        </div>
                      </div>
                      <div className="space-y-2 text-center">
                        <p className="text-xs font-semibold text-primary">Grad-CAM++ Heatmap</p>
                        <div className="aspect-square rounded-xl bg-black/50 border border-primary/30 overflow-hidden flex items-center justify-center p-1">
                          <img src={result.gradcam.heatmap} alt="Grad-CAM++ Heatmap" className="max-w-full max-h-full object-contain rounded-lg" />
                        </div>
                      </div>
                      <div className="space-y-2 text-center">
                        <p className="text-xs font-semibold text-emerald-400">Blended Overlay</p>
                        <div className="aspect-square rounded-xl bg-black/50 border border-emerald-500/30 overflow-hidden flex items-center justify-center p-1">
                          <img src={result.gradcam.overlay} alt="Grad-CAM++ Overlay" className="max-w-full max-h-full object-contain rounded-lg" />
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2 text-center max-w-lg mx-auto">
                      <p className="text-xs font-semibold text-primary capitalize">{activeTab} View</p>
                      <div className="aspect-square rounded-xl bg-black/50 border border-white/10 overflow-hidden flex items-center justify-center p-2">
                        <img 
                          src={activeTab === 'overlay' ? result.gradcam.overlay : activeTab === 'heatmap' ? result.gradcam.heatmap : result.gradcam.original} 
                          alt={activeTab} 
                          className="max-w-full max-h-full object-contain rounded-lg" 
                        />
                      </div>
                    </div>
                  )}

                  {/* Heatmap Legend */}
                  <div className="p-4 bg-white/5 rounded-xl border border-white/5 space-y-2">
                    <div className="flex justify-between items-center text-xs text-muted-foreground font-medium">
                      <span>Low contribution</span>
                      <span className="font-semibold text-foreground">Grad-CAM++ Model Contribution Scale</span>
                      <span>High contribution</span>
                    </div>
                    <div className="h-3 rounded-full w-full bg-gradient-to-r from-blue-600 via-cyan-400 via-yellow-400 to-red-600 shadow-inner"></div>
                    <p className="text-[11px] text-muted-foreground text-center italic">
                      The highlighted regions indicate areas that contributed strongly to the model's prediction for the selected class.
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Model Attention vs Explanation Comparison Section */}
              <Card className="border-white/10">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-semibold flex items-center gap-2">
                    <Layers className="w-4 h-4 text-primary" /> Model Attention vs Explanation
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-primary uppercase tracking-wider">Adaptive Attention Map</h4>
                        <span className="text-[10px] bg-primary/20 text-primary px-2 py-0.5 rounded font-mono">Internal Mechanism</span>
                      </div>
                      <div className="aspect-square rounded-lg bg-black/60 border border-white/10 overflow-hidden flex items-center justify-center">
                        {result.attention && result.attention.spatial_heatmap ? (
                          <img src={result.attention.spatial_heatmap} alt="Adaptive Attention" className="max-w-full max-h-full object-contain" />
                        ) : (
                          <div className="p-4 text-xs text-muted-foreground text-center">
                            Attention map unavailable in standard baseline mode. Switch to MODEL_MODE=attention.
                          </div>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        <strong className="text-foreground">Adaptive Attention:</strong> Learned internal feature reweighting applied dynamically during model forward pass.
                      </p>
                    </div>

                    <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Grad-CAM++ Map</h4>
                        <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded font-mono">Post-hoc Explanation</span>
                      </div>
                      <div className="aspect-square rounded-lg bg-black/60 border border-white/10 overflow-hidden flex items-center justify-center">
                        <img src={result.gradcam.heatmap} alt="Grad-CAM++ Explanation" className="max-w-full max-h-full object-contain" />
                      </div>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        <strong className="text-foreground">Grad-CAM++:</strong> Post-hoc class-specific explanation based on feature activations and backward gradients.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
