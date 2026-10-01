import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { 
  getResearchMetrics, 
  getModelComparison, 
  getAblationStudy,
  getTrainingHistory,
  getHistoryStats,
  ResearchMetricsResponse, 
  ModelComparisonResponse, 
  AblationStudyResponse 
} from "@/services/api"
import { AlertCircle, BarChart2, Layers, Cpu, Clock, Zap, Activity, Sparkles, Download, Database } from "lucide-react"

export default function Research() {
  const [metrics, setMetrics] = useState<ResearchMetricsResponse | null>(null)
  const [comparison, setComparison] = useState<ModelComparisonResponse | null>(null)
  const [ablation, setAblation] = useState<AblationStudyResponse | null>(null)
  const [history, setHistory] = useState<{ baseline: any; attention: any } | null>(null)
  const [loading, setLoading] = useState(true)
  const [sortField, setSortField] = useState<string>("f1-score")
  const [sortAsc, setSortAsc] = useState(false)

  const [historyStats, setHistoryStats] = useState<any | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [mRes, cRes, aRes, hRes, sRes] = await Promise.all([
          getResearchMetrics().catch(() => ({ status: "not_available", message: "Model evaluation not completed." })),
          getModelComparison().catch(() => ({ status: "not_available", message: "Model comparison not executed." })),
          getAblationStudy().catch(() => ({ status: "not_available", message: "Ablation study not executed." })),
          getTrainingHistory().catch(() => ({ baseline: null, attention: null })),
          getHistoryStats().catch(() => null)
        ])
        setMetrics(mRes)
        setComparison(cRes)
        setAblation(aRes)
        setHistory(hRes)
        setHistoryStats(sRes)
      } catch (err) {
        console.error("Failed to load research data:", err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const isMetricsAvailable = metrics && metrics.status === "available"
  const isCompAvailable = comparison && comparison.status === "available" && comparison.baseline && comparison.attention
  const isAblationAvailable = ablation && ablation.status === "available" && ablation.experiments

  // Calculate Delta Metrics
  const deltaAccuracy = isCompAvailable ? (comparison.attention!.accuracy - comparison.baseline!.accuracy) * 100 : null
  const deltaF1 = isCompAvailable ? comparison.attention!.f1_macro - comparison.baseline!.f1_macro : null
  const deltaParams = isCompAvailable ? comparison.attention!.total_parameters - comparison.baseline!.total_parameters : null
  const deltaLatency = isCompAvailable ? comparison.attention!.inference_time_ms_per_image - comparison.baseline!.inference_time_ms_per_image : null

  const exportCSV = () => {
    const csvRows = [
      ["Model Architecture", "Accuracy", "Macro Precision", "Macro Recall", "Macro F1", "Parameters", "Latency (ms)"],
      [
        "EfficientNetV2-S Baseline",
        isCompAvailable ? `${(comparison.baseline!.accuracy * 100).toFixed(2)}%` : "N/A",
        isCompAvailable ? comparison.baseline!.precision_macro.toFixed(4) : "N/A",
        isCompAvailable ? comparison.baseline!.recall_macro.toFixed(4) : "N/A",
        isCompAvailable ? comparison.baseline!.f1_macro.toFixed(4) : "N/A",
        isCompAvailable ? comparison.baseline!.total_parameters : "20177248",
        isCompAvailable ? comparison.baseline!.inference_time_ms_per_image : "N/A"
      ],
      [
        "EfficientNetV2-S + Adaptive Attention",
        isCompAvailable ? `${(comparison.attention!.accuracy * 100).toFixed(2)}%` : "N/A",
        isCompAvailable ? comparison.attention!.precision_macro.toFixed(4) : "N/A",
        isCompAvailable ? comparison.attention!.recall_macro.toFixed(4) : "N/A",
        isCompAvailable ? comparison.attention!.f1_macro.toFixed(4) : "N/A",
        isCompAvailable ? comparison.attention!.total_parameters : "20341833",
        isCompAvailable ? comparison.attention!.inference_time_ms_per_image : "N/A"
      ]
    ]

    const blob = new Blob([csvRows.map(e => e.join(",")).join("\n")], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `PlantIntel_Research_Comparison_${Date.now()}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const exportJSON = () => {
    const data = {
      comparison: comparison ?? "N/A",
      ablation: ablation ?? "N/A",
      metrics: metrics ?? "N/A",
      history: history ?? "N/A"
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `PlantIntel_Research_Data_${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Handle class report sorting
  const getClassReportArray = () => {
    if (!isMetricsAvailable || !metrics.classification_report) return []
    const entries = Object.entries(metrics.classification_report).filter(
      ([key]) => !["accuracy", "macro avg", "weighted avg"].includes(key)
    )

    return entries.sort((a, b) => {
      const valA = a[1][sortField] ?? 0
      const valB = b[1][sortField] ?? 0
      return sortAsc ? valA - valB : valB - valA
    })
  }

  const classReport = getClassReportArray()

  return (
    <div className="space-y-8 pb-12">
      {/* HEADER SECTION */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <h1 className="text-3xl font-black tracking-tight flex items-center gap-3">
            <BarChart2 className="w-8 h-8 text-primary" />
            Research & Experimental Dashboard
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Empirical evaluation metrics comparing baseline EfficientNetV2-S against proposed Adaptive Lightweight Attention.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={exportCSV} className="text-xs border-white/10">
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export CSV
          </Button>
          <Button variant="outline" size="sm" onClick={exportJSON} className="text-xs border-white/10">
            <Download className="w-3.5 h-3.5 mr-1.5" /> Export JSON
          </Button>
        </div>
      </div>

      {!loading && !isMetricsAvailable && !isCompAvailable && (
        <Card className="border-warning/30 bg-warning/5">
          <CardContent className="p-6 flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-warning flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-warning">Experimental Evaluation Not Completed</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Run the dataset training and ablation experiment scripts to generate empirical research metrics.
              </p>
              <p className="text-xs text-muted-foreground mt-3 bg-black/30 p-2.5 rounded font-mono">
                Execution Commands:<br/>
                1. <code>python training/inspect_dataset.py</code><br/>
                2. <code>python training/train.py</code> (Baseline)<br/>
                3. <code>python training/train_attention.py</code> (Proposed Attention Model)<br/>
                4. <code>python training/ablation.py</code> (Ablation Experiments & Model Comparison)
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* RESEARCH SUMMARY COMPACT CARD */}
      <Card className="border-white/10 bg-card/60">
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-mono uppercase tracking-wider text-muted-foreground flex items-center gap-2">
            <Database className="w-4 h-4 text-primary" /> Capstone Research Project Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-2">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="p-3 bg-white/5 rounded-lg">
              <span className="text-muted-foreground block">Dataset</span>
              <strong className="text-foreground text-sm font-semibold">PlantVillage Benchmark</strong>
            </div>
            <div className="p-3 bg-white/5 rounded-lg">
              <span className="text-muted-foreground block">Classes Analyzed</span>
              <strong className="text-foreground text-sm font-semibold">{isMetricsAvailable && metrics.classification_report ? Object.keys(metrics.classification_report).length - 3 : '38 Plant Disease Classes'}</strong>
            </div>
            <div className="p-3 bg-white/5 rounded-lg">
              <span className="text-muted-foreground block">Backbone Architecture</span>
              <strong className="text-foreground text-sm font-semibold">EfficientNetV2-S</strong>
            </div>
            <div className="p-3 bg-white/5 rounded-lg">
              <span className="text-muted-foreground block">Proposed Innovation</span>
              <strong className="text-primary text-sm font-semibold">Adaptive Lightweight Attention</strong>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* DATABASE USER HISTORY ANALYTICS */}
      {historyStats && (
        <Card className="border-white/10 bg-card/40">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-muted-foreground flex items-center justify-between">
              <span className="flex items-center gap-2">Database User Activity Statistics</span>
              <span className="text-[10px] text-muted-foreground font-sans">User History Analytics (Distinct from Benchmark Test Set Accuracy)</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-2">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
              <div className="p-3 bg-white/5 rounded-lg">
                <span className="text-muted-foreground font-sans block">Total Analyses Saved</span>
                <strong className="text-lg font-bold text-foreground">{historyStats.total_analyses}</strong>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <span className="text-muted-foreground font-sans block">Diseases Detected</span>
                <strong className="text-lg font-bold text-foreground">{historyStats.diseases_detected_count}</strong>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <span className="text-muted-foreground font-sans block">Average Affected Area</span>
                <strong className="text-lg font-bold text-emerald-400">{historyStats.average_severity_percentage}%</strong>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <span className="text-muted-foreground font-sans block">Database Storage</span>
                <strong className="text-sm font-bold text-primary font-sans">SQLite Persistent DB</strong>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* MODEL ARCHITECTURE COMPARISON + DELTA METRICS */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Zap className="w-5 h-5 text-primary" />
            Model Architecture Comparison (Baseline vs Proposed)
          </h2>
          <span className="text-xs font-mono text-muted-foreground">Raw Experimental Measurements</span>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Baseline Card */}
          <Card className="border-white/10 bg-card/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-mono uppercase tracking-wider text-muted-foreground flex justify-between">
                <span>Baseline Model</span>
                <span className="text-xs font-normal text-muted-foreground px-2 py-0.5 bg-white/5 rounded">Standard</span>
              </CardTitle>
              <h3 className="text-xl font-bold mt-1 text-foreground">EfficientNetV2-S</h3>
            </CardHeader>
            <CardContent className="pt-2 space-y-4">
              <div className="grid grid-cols-2 gap-3 text-sm font-mono">
                <div className="bg-white/5 p-3 rounded-lg">
                  <span className="text-xs text-muted-foreground font-sans block">Accuracy</span>
                  <span className="text-xl font-bold text-foreground">
                    {isCompAvailable ? `${(comparison.baseline!.accuracy * 100).toFixed(2)}%` : '--'}
                  </span>
                </div>
                <div className="bg-white/5 p-3 rounded-lg">
                  <span className="text-xs text-muted-foreground font-sans block">Macro F1 Score</span>
                  <span className="text-xl font-bold text-foreground">
                    {isCompAvailable ? comparison.baseline!.f1_macro.toFixed(4) : '--'}
                  </span>
                </div>
                <div className="bg-white/5 p-3 rounded-lg">
                  <span className="text-xs text-muted-foreground font-sans block">Total Parameters</span>
                  <span className="text-sm font-semibold text-foreground">
                    {isCompAvailable ? comparison.baseline!.total_parameters.toLocaleString() : '20,177,248'}
                  </span>
                </div>
                <div className="bg-white/5 p-3 rounded-lg">
                  <span className="text-xs text-muted-foreground font-sans block">Inference Latency</span>
                  <span className="text-sm font-semibold text-foreground">
                    {isCompAvailable ? `${comparison.baseline!.inference_time_ms_per_image} ms` : '--'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Proposed Attention Card */}
          <Card className="border-primary/40 bg-primary/5 shadow-[0_0_20px_rgba(20,180,100,0.08)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-mono uppercase tracking-wider text-primary flex justify-between">
                <span>Proposed Model</span>
                <span className="text-xs font-normal text-primary px-2 py-0.5 bg-primary/20 rounded">Proposed</span>
              </CardTitle>
              <h3 className="text-xl font-bold mt-1 text-primary">EfficientNetV2-S + Adaptive Attention</h3>
            </CardHeader>
            <CardContent className="pt-2 space-y-4">
              <div className="grid grid-cols-2 gap-3 text-sm font-mono">
                <div className="bg-white/5 p-3 rounded-lg">
                  <span className="text-xs text-muted-foreground font-sans block">Accuracy</span>
                  <span className="text-xl font-bold text-primary">
                    {isCompAvailable ? `${(comparison.attention!.accuracy * 100).toFixed(2)}%` : '--'}
                  </span>
                </div>
                <div className="bg-white/5 p-3 rounded-lg">
                  <span className="text-xs text-muted-foreground font-sans block">Macro F1 Score</span>
                  <span className="text-xl font-bold text-primary">
                    {isCompAvailable ? comparison.attention!.f1_macro.toFixed(4) : '--'}
                  </span>
                </div>
                <div className="bg-white/5 p-3 rounded-lg">
                  <span className="text-xs text-muted-foreground font-sans block">Total Parameters</span>
                  <span className="text-sm font-semibold text-primary">
                    {isCompAvailable ? comparison.attention!.total_parameters.toLocaleString() : '20,341,833'}
                  </span>
                </div>
                <div className="bg-white/5 p-3 rounded-lg">
                  <span className="text-xs text-muted-foreground font-sans block">Inference Latency</span>
                  <span className="text-sm font-semibold text-primary">
                    {isCompAvailable ? `${comparison.attention!.inference_time_ms_per_image} ms` : '--'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* DELTA METRICS OVERLAY CARD */}
        {isCompAvailable && (
          <Card className="border-white/10 bg-white/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-mono uppercase tracking-wider text-muted-foreground">
                Actual Delta Measurements (Proposed − Baseline)
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-1">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono text-center">
                <div className="p-2.5 bg-black/40 rounded-lg">
                  <span className="text-muted-foreground block font-sans">Accuracy Delta</span>
                  <strong className={deltaAccuracy && deltaAccuracy >= 0 ? "text-primary text-sm" : "text-foreground text-sm"}>
                    {deltaAccuracy ? `${deltaAccuracy >= 0 ? '+' : ''}${deltaAccuracy.toFixed(2)}%` : 'N/A'}
                  </strong>
                </div>
                <div className="p-2.5 bg-black/40 rounded-lg">
                  <span className="text-muted-foreground block font-sans">F1 Score Delta</span>
                  <strong className={deltaF1 && deltaF1 >= 0 ? "text-primary text-sm" : "text-foreground text-sm"}>
                    {deltaF1 ? `${deltaF1 >= 0 ? '+' : ''}${deltaF1.toFixed(4)}` : 'N/A'}
                  </strong>
                </div>
                <div className="p-2.5 bg-black/40 rounded-lg">
                  <span className="text-muted-foreground block font-sans">Parameter Overhead</span>
                  <strong className="text-muted-foreground text-sm">
                    {deltaParams ? `+${deltaParams.toLocaleString()} (+${((deltaParams / comparison.baseline!.total_parameters) * 100).toFixed(2)}%)` : 'N/A'}
                  </strong>
                </div>
                <div className="p-2.5 bg-black/40 rounded-lg">
                  <span className="text-muted-foreground block font-sans">Latency Difference</span>
                  <strong className="text-muted-foreground text-sm">
                    {deltaLatency ? `${deltaLatency >= 0 ? '+' : ''}${deltaLatency.toFixed(2)} ms` : 'N/A'}
                  </strong>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* ABLATION STUDY TABLE */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Layers className="w-5 h-5 text-primary" />
          Ablation Study Experiments
        </h2>

        <Card className="border-white/10">
          <CardContent className="p-0 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/5 border-b border-white/10 text-muted-foreground text-xs uppercase tracking-wider font-mono">
                <tr>
                  <th className="p-4 font-semibold">Model Variant</th>
                  <th className="p-4 font-semibold">Accuracy</th>
                  <th className="p-4 font-semibold">Macro F1</th>
                  <th className="p-4 font-semibold">Total Parameters</th>
                  <th className="p-4 font-semibold">Inference Latency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-mono text-xs">
                {isAblationAvailable ? (
                  Object.entries(ablation.experiments!).map(([key, exp]) => (
                    <tr key={key} className={key === 'adaptive_attention' ? 'bg-primary/10 font-semibold' : ''}>
                      <td className="p-4 font-sans font-medium text-foreground">{exp.model_name}</td>
                      <td className="p-4">{exp.accuracy ? `${(exp.accuracy * 100).toFixed(2)}%` : 'N/A'}</td>
                      <td className="p-4">{exp.f1_macro ? exp.f1_macro.toFixed(4) : 'N/A'}</td>
                      <td className="p-4">{exp.total_parameters ? exp.total_parameters.toLocaleString() : 'N/A'}</td>
                      <td className="p-4">{exp.inference_time_ms_per_image ? `${exp.inference_time_ms_per_image} ms` : 'N/A'}</td>
                    </tr>
                  ))
                ) : (
                  <>
                    <tr>
                      <td className="p-4 font-sans font-medium">EfficientNetV2-S Baseline</td>
                      <td className="p-4">N/A</td>
                      <td className="p-4">N/A</td>
                      <td className="p-4">20,177,248</td>
                      <td className="p-4">N/A</td>
                    </tr>
                    <tr>
                      <td className="p-4 font-sans font-medium">+ Channel Attention Only</td>
                      <td className="p-4">N/A</td>
                      <td className="p-4">N/A</td>
                      <td className="p-4">20,332,608</td>
                      <td className="p-4">N/A</td>
                    </tr>
                    <tr>
                      <td className="p-4 font-sans font-medium">+ Spatial Attention Only</td>
                      <td className="p-4">N/A</td>
                      <td className="p-4">N/A</td>
                      <td className="p-4">20,177,347</td>
                      <td className="p-4">N/A</td>
                    </tr>
                    <tr className="bg-primary/10">
                      <td className="p-4 font-sans font-semibold text-primary">+ Adaptive Lightweight Attention (Combined)</td>
                      <td className="p-4">N/A</td>
                      <td className="p-4">N/A</td>
                      <td className="p-4">20,341,833</td>
                      <td className="p-4">N/A</td>
                    </tr>
                  </>
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>

      {/* EXPLAINABILITY EVALUATION (PHASE 7) */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          Explainability Evaluation (Phase 7)
        </h2>

        <Card className="bg-card/50 border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-primary">
              Grad-CAM++ Post-hoc Explanation Framework
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div className="bg-white/5 p-3 rounded-lg">
                <span className="text-xs text-muted-foreground block font-sans">Explanation Method</span>
                <span className="text-base font-bold text-primary font-mono">Grad-CAM++</span>
              </div>
              <div className="bg-white/5 p-3 rounded-lg">
                <span className="text-xs text-muted-foreground block font-sans">Target Layer</span>
                <span className="text-base font-mono font-bold text-foreground">backbone[-1] / features[-1]</span>
              </div>
              <div className="bg-white/5 p-3 rounded-lg">
                <span className="text-xs text-muted-foreground block font-sans">Segmentation IoU</span>
                <span className="text-base font-bold text-muted-foreground font-mono">N/A</span>
              </div>
              <div className="bg-white/5 p-3 rounded-lg">
                <span className="text-xs text-muted-foreground block font-sans">Dice Coefficient</span>
                <span className="text-base font-bold text-muted-foreground font-mono">N/A</span>
              </div>
            </div>

            <div className="p-3 bg-white/5 rounded-lg text-xs text-muted-foreground space-y-1">
              <p><strong className="text-foreground">Evaluation Note:</strong> Ground-truth explanation annotations were not provided in the benchmark dataset. Explanation localization metrics (IoU / Dice) are reported as N/A.</p>
              <p>Grad-CAM++ visualizes model feature contributions directly from activations and backward gradients of the final convolutional block.</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* TRAINING CURVES & CONFUSION MATRIX */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Training Curves */}
        <Card className="border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Clock className="w-4 h-4 text-primary" /> Training History Curves
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-2">
            {isMetricsAvailable && metrics.training_history ? (
              <div className="space-y-3 font-mono text-xs max-h-56 overflow-y-auto bg-black/40 p-4 rounded-lg">
                {metrics.training_history.epochs.map((ep, i) => (
                  <div key={ep} className="flex justify-between border-b border-white/5 py-1">
                    <span>Epoch {ep}</span>
                    <span className="text-muted-foreground">Loss: {metrics.training_history?.train_loss[i]}</span>
                    <span className="text-primary">Val Acc: {((metrics.training_history?.val_accuracy[i] || 0) * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-muted-foreground border border-dashed border-white/10 rounded-lg">
                No training history available. Run training scripts to log epoch history.
              </div>
            )}
          </CardContent>
        </Card>

        {/* Confusion Matrix Artifact */}
        <Card className="border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Cpu className="w-4 h-4 text-primary" /> Confusion Matrix Artifact
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-2">
            {isMetricsAvailable ? (
              <div className="p-6 bg-primary/10 border border-primary/20 rounded-lg text-xs text-primary text-center space-y-2">
                <p className="font-semibold">Confusion matrix visual artifact saved.</p>
                <p className="font-mono text-[11px] text-muted-foreground">Path: models/confusion_matrix.png</p>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-muted-foreground border border-dashed border-white/10 rounded-lg">
                Confusion matrix image will be generated after dataset evaluation.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* CLASS PERFORMANCE TABLE */}
      {isMetricsAvailable && classReport.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary" />
            Class-wise Performance Metrics
          </h2>

          <Card className="border-white/10">
            <CardContent className="p-0 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-white/5 border-b border-white/10 text-muted-foreground text-xs uppercase tracking-wider font-mono">
                  <tr>
                    <th className="p-4 font-semibold">Disease Class</th>
                    <th 
                      className="p-4 font-semibold cursor-pointer hover:text-foreground"
                      onClick={() => { setSortField("precision"); setSortAsc(!sortAsc); }}
                    >
                      Precision {sortField === "precision" && (sortAsc ? "▲" : "▼")}
                    </th>
                    <th 
                      className="p-4 font-semibold cursor-pointer hover:text-foreground"
                      onClick={() => { setSortField("recall"); setSortAsc(!sortAsc); }}
                    >
                      Recall {sortField === "recall" && (sortAsc ? "▲" : "▼")}
                    </th>
                    <th 
                      className="p-4 font-semibold cursor-pointer hover:text-foreground"
                      onClick={() => { setSortField("f1-score"); setSortAsc(!sortAsc); }}
                    >
                      F1 Score {sortField === "f1-score" && (sortAsc ? "▲" : "▼")}
                    </th>
                    <th className="p-4 font-semibold">Support</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 font-mono text-xs">
                  {classReport.map(([cls, row]: any) => (
                    <tr key={cls} className="hover:bg-white/5 transition-colors">
                      <td className="p-4 font-sans font-medium text-foreground capitalize">
                        {cls.replace('___', ' - ').replace(/_/g, ' ')}
                      </td>
                      <td className="p-4">{(row.precision * 100).toFixed(2)}%</td>
                      <td className="p-4">{(row.recall * 100).toFixed(2)}%</td>
                      <td className="p-4 font-bold text-primary">{(row['f1-score'] * 100).toFixed(2)}%</td>
                      <td className="p-4 text-muted-foreground">{row.support}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
