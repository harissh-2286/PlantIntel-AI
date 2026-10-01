import { useState, useRef, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { UploadCloud, CheckCircle2, FileImage, Cpu, AlertTriangle, XCircle, FileWarning, Server, Activity, Sparkles } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { checkImageQuality, QualityResponse, analyzeFullPipeline, AnalyzeFullResponse, getModelInfo, ModelInfo } from "@/services/api"

export default function Analyze() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [dimensions, setDimensions] = useState<{w: number, h: number} | null>(null)
  const [status, setStatus] = useState<'idle' | 'checking' | 'classifying' | 'estimating_severity' | 'complete' | 'error'>('idle')
  const [quality, setQuality] = useState<QualityResponse | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalyzeFullResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null)
  const [modelError, setModelError] = useState<string | null>(null)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const fetchModel = async () => {
        try {
            const info = await getModelInfo()
            setModelInfo(info)
        } catch (err: any) {
            setModelError(err.message || "Unable to load model info.")
        }
    }
    fetchModel()
  }, [])

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!isDragging) setIsDragging(true)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFile = async (f: File) => {
    if (!f.type.startsWith('image/')) {
        setErrorMessage("Unsupported file type. Please upload JPG, JPEG, or PNG.")
        return;
    }
    if (f.size > 10 * 1024 * 1024) {
        setErrorMessage("Image is too large. Maximum file size is 10 MB.")
        return;
    }
    setErrorMessage(null)
    setFile(f)
    const objUrl = URL.createObjectURL(f)
    setPreview(objUrl)
    setStatus('idle')
    setQuality(null)
    setAnalysisResult(null)
    
    // Get dimensions
    const img = new Image()
    img.onload = () => {
        setDimensions({w: img.width, h: img.height})
    }
    img.src = objUrl

    setStatus('checking')
    try {
        const res = await checkImageQuality(f)
        setQuality(res)
    } catch (err: any) {
        setErrorMessage(err.message || "Something went wrong while analyzing the image.")
    } finally {
        setStatus('idle')
    }
  }

  const startFullAnalysis = async () => {
    if (!file || !quality?.valid || modelError) return
    
    setStatus('classifying')
    try {
        // Step 1: Classification & Severity full pipeline
        setTimeout(() => setStatus('estimating_severity'), 600)
        const res = await analyzeFullPipeline(file)
        setAnalysisResult(res)
        setStatus('complete')

        // Push to transient session history
        try {
          const raw = sessionStorage.getItem("plantintel_session_history")
          const hist = raw ? JSON.parse(raw) : []
          hist.unshift({
            timestamp: new Date().toLocaleString(),
            class_name: res.prediction.class_name,
            confidence: res.prediction.confidence,
            severity_percentage: res.severity.percentage,
            severity_level: res.severity.level
          })
          sessionStorage.setItem("plantintel_session_history", JSON.stringify(hist.slice(0, 20)))
        } catch (e) {
          console.error("Failed to write session history:", e)
        }
    } catch (err: any) {
        setErrorMessage(err.message || "Pipeline analysis failed.")
        setStatus('error')
    }
  }

  const clearImage = () => {
      setFile(null)
      setPreview(null)
      setStatus('idle')
      setQuality(null)
      setAnalysisResult(null)
      setErrorMessage(null)
      setDimensions(null)
      if (fileInputRef.current) {
          fileInputRef.current.value = ""
      }
  }
  
  const formatBytes = (bytes: number) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getSeverityBadgeColor = (level: string) => {
      switch (level) {
          case 'Minimal': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
          case 'Mild': return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
          case 'Moderate': return 'bg-warning/20 text-warning border-warning/30'
          case 'Severe': return 'bg-orange-500/20 text-orange-400 border-orange-500/30'
          case 'Very Severe': return 'bg-destructive/20 text-destructive border-destructive/30'
          default: return 'bg-muted text-muted-foreground'
      }
  }

  const getStepNumber = () => {
    if (!file) return 1
    if (status === 'checking') return 2
    if (status === 'classifying') return 3
    if (status === 'estimating_severity') return 4
    if (status === 'complete') return 6
    if (quality && quality.valid) return 2
    return 1
  }

  const currentStep = getStepNumber()

  const steps = [
    { num: '01', name: 'Upload' },
    { num: '02', name: 'Validate' },
    { num: '03', name: 'Classify' },
    { num: '04', name: 'Estimate Severity' },
    { num: '05', name: 'Explain' },
    { num: '06', name: 'Results' }
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analysis Workbench</h1>
        <p className="text-muted-foreground mt-2">Unified Pipeline: Image Validation → Adaptive Attention Classification → Disease Severity Estimation.</p>
      </div>

      {/* WORKFLOW STEP INDICATOR */}
      <div className="p-4 bg-card/60 border border-white/10 rounded-2xl">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-center text-xs font-semibold">
          {steps.map((s, idx) => {
            const stepNum = idx + 1
            const isActive = currentStep === stepNum
            const isDone = currentStep > stepNum
            return (
              <div 
                key={s.num}
                className={`p-2.5 rounded-xl border transition-all flex flex-col items-center justify-center gap-1 ${
                  isActive 
                    ? 'bg-primary/20 border-primary text-primary font-bold shadow-[0_0_12px_rgba(20,180,100,0.2)]' 
                    : isDone
                    ? 'bg-white/5 border-white/10 text-foreground'
                    : 'bg-white/5 border-white/5 text-muted-foreground opacity-50'
                }`}
              >
                <span className="font-mono text-[10px] block opacity-80">{s.num}</span>
                <span className="truncate w-full">{s.name}</span>
              </div>
            )
          })}
        </div>
      </div>
      
      {/* Model Status Card */}
      <Card className="bg-card/50 border-white/5">
        <CardContent className="p-4 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
           <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${modelInfo ? 'bg-primary animate-pulse' : 'bg-destructive'}`}></div>
              <h3 className="font-medium flex items-center gap-2"><Server className="w-4 h-4 text-muted-foreground" /> AI MODEL STATUS</h3>
           </div>
           
           {modelInfo ? (
               <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
                   <div className="flex items-center gap-1"><span className="font-semibold text-foreground">Backbone:</span> EfficientNetV2-S</div>
                   <div className="flex items-center gap-1"><span className="font-semibold text-foreground">Architecture:</span> {modelInfo.architecture || 'Adaptive Lightweight Attention'}</div>
                   <div className="flex items-center gap-1"><span className="font-semibold text-foreground">Framework:</span> {modelInfo.framework}</div>
                   <div className="flex items-center gap-1"><span className="font-semibold text-foreground">Weights:</span> {modelInfo.weights}</div>
                   <div className="flex items-center gap-1"><span className="font-semibold text-foreground">Device:</span> <span className="uppercase">{modelInfo.device}</span></div>
               </div>
           ) : (
               <div className="text-sm text-destructive">{modelError || "Loading model status..."}</div>
           )}
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Image Input</CardTitle>
            </CardHeader>
            <CardContent>
              {!preview ? (
                <div 
                  className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer group ${isDragging ? 'border-primary bg-primary/10' : 'border-white/10 hover:bg-white/5'}`}
                  onDragEnter={handleDragEnter}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input 
                    type="file" 
                    ref={fileInputRef}
                    className="hidden" 
                    accept="image/jpeg, image/png, image/jpg"
                    onChange={(e) => e.target.files && handleFile(e.target.files[0])}
                  />
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 transition-transform ${isDragging ? 'bg-primary/20 scale-110' : 'bg-primary/10 group-hover:scale-110'}`}>
                    <UploadCloud className={`w-8 h-8 ${isDragging ? 'text-primary' : 'text-primary'}`} />
                  </div>
                  <h3 className="text-lg font-medium mb-2">{isDragging ? 'Drop image to analyze' : 'Drag & drop your leaf image'}</h3>
                  <p className="text-sm text-muted-foreground">or click to browse files (JPG, PNG)</p>
                  {errorMessage && (
                      <p className="text-sm text-destructive mt-4">{errorMessage}</p>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="relative rounded-xl overflow-hidden aspect-video bg-black/50 border border-white/10 flex items-center justify-center group">
                    <img src={preview} alt="Upload preview" className="max-w-full max-h-full object-contain" />
                    <div className="absolute top-2 right-2 flex gap-2">
                      <Button 
                        variant="secondary" 
                        size="sm" 
                        className="bg-black/50 backdrop-blur hover:bg-black/70"
                        disabled={status !== 'idle'}
                        onClick={() => fileInputRef.current?.click()}
                      >
                        Replace
                      </Button>
                      <Button 
                        variant="secondary" 
                        size="sm" 
                        className="bg-destructive/80 text-destructive-foreground hover:bg-destructive"
                        disabled={status !== 'idle'}
                        onClick={clearImage}
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                  
                  <div className="bg-card border border-white/5 rounded-lg p-4 space-y-2">
                     <p className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Image Information</p>
                     <div className="grid grid-cols-2 gap-y-2 text-sm">
                         <div className="text-muted-foreground">Filename</div>
                         <div className="font-medium truncate" title={file?.name}>{file?.name}</div>
                         <div className="text-muted-foreground">File size</div>
                         <div className="font-medium">{file ? formatBytes(file.size) : '--'}</div>
                         <div className="text-muted-foreground">Dimensions</div>
                         <div className="font-medium">{dimensions ? `${dimensions.w} × ${dimensions.h}` : '--'}</div>
                         <div className="text-muted-foreground">Type</div>
                         <div className="font-medium">{file?.type.split('/')[1].toUpperCase()}</div>
                     </div>
                  </div>

                  {status === 'idle' && (
                    <Button 
                      onClick={startFullAnalysis} 
                      disabled={!quality?.valid || !!modelError}
                      className={`w-full h-12 ${quality?.valid && !modelError ? 'shadow-[0_0_15px_rgba(20,180,100,0.2)]' : ''}`}
                    >
                      <Cpu className="w-5 h-5 mr-2" /> 
                      Start Unified Analysis Pipeline
                    </Button>
                  )}
                  
                  {status === 'idle' && quality && !quality.valid && (
                      <p className="text-sm text-destructive text-center">Please upload a clearer image before continuing.</p>
                  )}
                  {status === 'idle' && quality && quality.valid && quality.warnings.length > 0 && (
                      <p className="text-sm text-warning text-center">Image quality is acceptable, but results may be less reliable.</p>
                  )}

                  {(status === 'classifying' || status === 'estimating_severity') && (
                    <div className="space-y-4 p-6 bg-card border border-white/5 rounded-xl text-center">
                      <div className="inline-flex w-12 h-12 rounded-full border-4 border-primary/30 border-t-primary animate-spin mb-4"></div>
                      <h3 className="text-lg font-medium">Executing Analysis Pipeline</h3>
                      <Progress value={status === 'classifying' ? 50 : 85} className="h-1.5" />
                      <div className="text-sm text-muted-foreground animate-pulse font-medium">
                        {status === 'classifying' ? 'Step 1/2: Disease Classification (EfficientNetV2-S + Attention)...' : 'Step 2/2: Estimating Leaf Affected Area & Severity...'}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div>
          <AnimatePresence mode="wait">
            {status === 'checking' && (
               <motion.div 
                 initial={{ opacity: 0 }}
                 animate={{ opacity: 1 }}
                 exit={{ opacity: 0 }}
                 className="h-full flex flex-col items-center justify-center text-center p-12 border border-dashed border-white/5 rounded-xl bg-card/30"
               >
                 <div className="inline-flex w-12 h-12 rounded-full border-4 border-primary/30 border-t-primary animate-spin mb-4"></div>
                 <h3 className="text-lg font-medium">Validating image quality...</h3>
               </motion.div>
            )}

            {status === 'idle' && quality && (
              <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <Card className={`border-t-4 shadow-lg ${quality.valid ? (quality.warnings.length > 0 ? 'border-t-warning shadow-[0_10px_30px_rgba(250,180,0,0.1)]' : 'border-t-primary shadow-[0_10px_30px_rgba(20,180,100,0.1)]') : 'border-t-destructive shadow-[0_10px_30px_rgba(220,38,38,0.1)]'}`}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground flex justify-between">
                      Image Quality Check
                      <span className={quality.quality_score >= 80 ? 'text-primary' : quality.quality_score >= 50 ? 'text-warning' : 'text-destructive'}>
                        {quality.quality_score} / 100
                      </span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-3 mb-6">
                      {quality.valid ? (
                         quality.warnings.length > 0 ? (
                           <>
                             <div className="w-10 h-10 rounded-full bg-warning/20 flex items-center justify-center">
                               <AlertTriangle className="w-5 h-5 text-warning" />
                             </div>
                             <div>
                               <h2 className="text-xl font-bold text-warning">Acceptable Quality</h2>
                               <p className="text-sm text-muted-foreground">Ready for Analysis</p>
                             </div>
                           </>
                         ) : (
                           <>
                             <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                               <CheckCircle2 className="w-5 h-5 text-primary" />
                             </div>
                             <div>
                               <h2 className="text-xl font-bold text-primary">Excellent Quality</h2>
                               <p className="text-sm text-muted-foreground">Ready for Analysis</p>
                             </div>
                           </>
                         )
                      ) : (
                         <>
                           <div className="w-10 h-10 rounded-full bg-destructive/20 flex items-center justify-center">
                             <XCircle className="w-5 h-5 text-destructive" />
                           </div>
                           <div>
                             <h2 className="text-xl font-bold text-destructive">Unsuitable Quality</h2>
                             <p className="text-sm text-muted-foreground">Cannot be analyzed reliably</p>
                           </div>
                         </>
                      )}
                    </div>
                    
                    <div className="space-y-3">
                       <p className="text-sm font-medium">Validation Checks:</p>
                       <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                          <div className={`flex items-center gap-2 ${quality.checks.format ? 'text-primary' : 'text-destructive'}`}>
                            {quality.checks.format ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />} File format
                          </div>
                          <div className={`flex items-center gap-2 ${quality.checks.resolution ? 'text-primary' : 'text-destructive'}`}>
                            {quality.checks.resolution ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />} Resolution
                          </div>
                          <div className={`flex items-center gap-2 ${quality.blur_status === 'good' ? 'text-primary' : quality.blur_status === 'warning' ? 'text-warning' : 'text-destructive'}`}>
                            {quality.blur_status === 'good' ? <CheckCircle2 className="w-4 h-4" /> : quality.blur_status === 'warning' ? <AlertTriangle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />} Sharpness
                          </div>
                          <div className={`flex items-center gap-2 ${quality.brightness_status === 'good' ? 'text-primary' : quality.brightness_status === 'warning' ? 'text-warning' : 'text-destructive'}`}>
                            {quality.brightness_status === 'good' ? <CheckCircle2 className="w-4 h-4" /> : quality.brightness_status === 'warning' ? <AlertTriangle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />} Brightness
                          </div>
                       </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {status === 'complete' && analysisResult && (
              <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                {/* CARD 1: DISEASE CLASSIFICATION */}
                <Card className="border-t-primary border-t-4 shadow-lg">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs font-semibold uppercase tracking-wider text-primary flex items-center gap-2">
                      <Cpu className="w-4 h-4" /> 1. Disease Classification
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-2">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h2 className="text-2xl font-bold capitalize">{analysisResult.prediction.class_name.replace('ImageNet class: ', '').replace(/___/g, ' - ').replace(/_/g, ' ')}</h2>
                        <span className="px-2 py-0.5 rounded-full bg-primary/20 text-primary text-[10px] font-bold uppercase tracking-wider mt-1 inline-block">
                          {analysisResult.model.architecture}
                        </span>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-muted-foreground mb-1">Confidence</p>
                        <div className={`text-xl font-bold ${analysisResult.prediction.confidence < 0.50 ? 'text-warning' : 'text-primary'}`}>
                          {(analysisResult.prediction.confidence * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <p className="text-xs font-medium text-muted-foreground">Top Alternatives</p>
                      {analysisResult.top_predictions.slice(1, 4).map((p: any, i: number) => (
                        <div key={i} className="flex items-center gap-2 text-xs">
                          <span className="w-36 truncate capitalize">{p.class_name.replace('ImageNet class: ', '').replace(/___/g, ' - ').replace(/_/g, ' ')}</span>
                          <Progress value={p.confidence * 100} className="flex-1 bg-white/5 h-1" />
                          <span className="w-10 text-right opacity-70">{(p.confidence * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>

                    <div className="mt-4 pt-3 border-t border-white/10 flex gap-2">
                      <Button 
                        onClick={() => navigate('/explainability', { state: { file } })}
                        className="flex-1 text-xs font-semibold bg-primary/20 hover:bg-primary/30 text-primary border border-primary/30"
                      >
                        <Sparkles className="w-4 h-4 mr-2" /> Explain (Grad-CAM++)
                      </Button>
                      <Button 
                        onClick={() => navigate('/results', { state: { analysisResult, file } })}
                        className="flex-1 text-xs font-semibold bg-white/10 hover:bg-white/20 text-foreground border border-white/10"
                      >
                        View Full Report
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* CARD 2: DISEASE SEVERITY ESTIMATION */}
                <Card className="border-t-secondary border-t-4 shadow-lg">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs font-semibold uppercase tracking-wider text-secondary flex items-center justify-between">
                      <span className="flex items-center gap-2"><Activity className="w-4 h-4" /> 2. Affected Area & Severity</span>
                      <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${getSeverityBadgeColor(analysisResult.severity.level)}`}>
                        {analysisResult.severity.level} Severity
                      </span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-2 space-y-4">
                    <div className="flex items-center justify-between bg-white/5 p-4 rounded-xl">
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Estimated Affected Leaf Area</p>
                        <div className="text-3xl font-bold text-secondary">
                          {analysisResult.severity.percentage.toFixed(2)}%
                        </div>
                      </div>
                      <div className="w-32">
                        <Progress value={analysisResult.severity.percentage} className="h-3 bg-white/10" />
                        <p className="text-[10px] text-muted-foreground text-center mt-1 font-mono">
                          {analysisResult.area.affected_pixels.toLocaleString()} / {analysisResult.area.leaf_pixels.toLocaleString()} px
                        </p>
                      </div>
                    </div>

                    {analysisResult.severity_visualization && (
                      <div className="space-y-2">
                        <p className="text-xs font-semibold text-muted-foreground">Estimated Affected Region Mask (Red Highlight)</p>
                        <div className="aspect-video rounded-xl bg-black/60 border border-white/10 overflow-hidden flex items-center justify-center">
                          <img src={analysisResult.severity_visualization} alt="Estimated affected region" className="max-w-full max-h-full object-contain" />
                        </div>
                      </div>
                    )}

                    {analysisResult.severity_status === "unreliable" && (
                      <div className="p-3 bg-warning/10 border border-warning/20 rounded-lg text-xs text-warning flex items-start gap-2">
                        <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                        <div>{analysisResult.severity_message || "Severity estimation may be less reliable for this image."}</div>
                      </div>
                    )}

                    {/* Scientific Disclaimer */}
                    <div className="p-3 bg-card border border-white/5 rounded-lg text-[11px] text-muted-foreground">
                      <span className="font-semibold text-foreground">Scientific Disclaimer:</span> Severity is an estimated affected-area measurement based on the configured image-analysis method and has not been validated against expert pixel-level annotations.
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
          
          {status === 'error' && (
            <div className="h-full flex flex-col items-center justify-center text-center p-12 border border-dashed border-destructive/30 rounded-xl bg-destructive/5">
              <div className="w-16 h-16 rounded-full bg-destructive/20 flex items-center justify-center mb-4 text-destructive">
                <FileWarning className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-medium text-destructive mb-2">Analysis Error</h3>
              <p className="text-sm text-muted-foreground max-w-[250px]">{errorMessage}</p>
            </div>
          )}
          
          {!file && status === 'idle' && (
            <div className="h-full flex flex-col items-center justify-center text-center p-12 border border-dashed border-white/5 rounded-xl bg-card/30">
              <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4 text-muted-foreground">
                <FileImage className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-medium mb-2">Awaiting Image</h3>
              <p className="text-sm text-muted-foreground max-w-[250px]">
                Upload a leaf image to evaluate quality, perform disease classification, and estimate affected area severity.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
