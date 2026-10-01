import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowRight, BrainCircuit, ScanSearch, Sparkles, CheckCircle2, ShieldCheck, Layers, Eye, Activity } from "lucide-react"
import { Link } from "react-router-dom"

export default function Home() {
  return (
    <div className="space-y-12 pb-12">
      {/* HERO SECTION */}
      <section className="relative overflow-hidden rounded-3xl p-8 lg:p-12 bg-gradient-to-br from-card via-card/80 to-primary/10 border border-white/10 shadow-2xl">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/20 text-primary text-xs font-semibold uppercase tracking-wider mb-6 border border-primary/30">
            <Sparkles className="w-3.5 h-3.5" /> PlantIntel AI • Capstone Platform
          </div>
          
          <h1 className="text-4xl lg:text-6xl font-black tracking-tight mb-4 text-foreground leading-none">
            PlantIntel <span className="text-primary">AI</span>
          </h1>
          
          <h2 className="text-xl lg:text-2xl font-bold text-muted-foreground mb-4">
            Explainable Deep Learning for Plant Disease Intelligence
          </h2>
          
          <p className="text-base lg:text-lg text-muted-foreground mb-8 leading-relaxed max-w-2xl">
            Detect disease, estimate affected area, and understand the visual evidence behind the model prediction.
          </p>
          
          <div className="flex flex-wrap items-center gap-4">
            <Link to="/analyze">
              <Button size="lg" className="h-12 px-8 text-base bg-primary hover:bg-primary/90 text-primary-foreground font-semibold shadow-lg shadow-primary/25">
                Analyze a Leaf <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link to="/research">
              <Button variant="outline" size="lg" className="h-12 px-8 text-base border-white/10 hover:bg-white/5 font-semibold">
                Explore Research
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CORE CAPABILITIES GRID */}
      <section className="grid md:grid-cols-3 gap-6">
        <Card className="h-full bg-card/60 border-t-4 border-t-primary border-white/10">
          <CardHeader>
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-3 border border-primary/20">
              <BrainCircuit className="w-6 h-6 text-primary" />
            </div>
            <CardTitle className="text-xl font-bold">Fine-tuned Classification</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground leading-relaxed">
              EfficientNetV2-S backbone augmented with proposed Adaptive Lightweight Attention for robust plant disease identification across leaf species.
            </p>
          </CardContent>
        </Card>

        <Card className="h-full bg-card/60 border-t-4 border-t-emerald-400 border-white/10">
          <CardHeader>
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-3 border border-emerald-500/20">
              <Activity className="w-6 h-6 text-emerald-400" />
            </div>
            <CardTitle className="text-xl font-bold">Severity Estimation</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Image analysis pipeline isolating leaf area boundaries vs chlorosis/necrosis affected regions to estimate affected percentage and severity category.
            </p>
          </CardContent>
        </Card>

        <Card className="h-full bg-card/60 border-t-4 border-t-cyan-400 border-white/10">
          <CardHeader>
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center mb-3 border border-cyan-500/20">
              <ScanSearch className="w-6 h-6 text-cyan-400" />
            </div>
            <CardTitle className="text-xl font-bold">Grad-CAM++ XAI</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Post-hoc class-specific visual explanations generated directly from convolutional feature activations and 2nd-order backward gradients.
            </p>
          </CardContent>
        </Card>
      </section>
      
      {/* POLISHED END-TO-END ARCHITECTURE DIAGRAM */}
      <section>
        <Card className="overflow-hidden bg-card/80 border-white/10">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl font-bold flex items-center gap-2">
              <Layers className="w-5 h-5 text-primary" /> End-to-End Deep Learning Architecture
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Complete data pipeline from leaf image input to quality check, attention feature refinement, classification, severity, and post-hoc XAI.
            </p>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-6">
              {/* Sequential Flow Nodes */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Node 1 */}
                <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center space-y-2 relative">
                  <span className="text-[10px] font-mono text-muted-foreground uppercase block">Input Step 01</span>
                  <div className="w-8 h-8 rounded-lg bg-primary/20 text-primary mx-auto flex items-center justify-center">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <h4 className="text-sm font-bold">Leaf Image Input</h4>
                  <p className="text-[11px] text-muted-foreground">User upload (Supports all image formats)</p>
                </div>

                {/* Node 2 */}
                <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center space-y-2 relative">
                  <span className="text-[10px] font-mono text-muted-foreground uppercase block">Validation Step 02</span>
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <h4 className="text-sm font-bold">Quality Validation</h4>
                  <p className="text-[11px] text-muted-foreground">Blur, resolution, contrast & brightness</p>
                </div>

                {/* Node 3 */}
                <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center space-y-2 relative">
                  <span className="text-[10px] font-mono text-muted-foreground uppercase block">Backbone Step 03</span>
                  <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 mx-auto flex items-center justify-center">
                    <BrainCircuit className="w-4 h-4" />
                  </div>
                  <h4 className="text-sm font-bold">EfficientNetV2-S</h4>
                  <p className="text-[11px] text-muted-foreground">Convolutional feature extraction</p>
                </div>

                {/* Node 4 */}
                <div className="p-4 rounded-xl bg-white/5 border border-primary/30 bg-primary/5 text-center space-y-2 relative">
                  <span className="text-[10px] font-mono text-primary uppercase block font-semibold">Proposed Step 04</span>
                  <div className="w-8 h-8 rounded-lg bg-primary/20 text-primary mx-auto flex items-center justify-center">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <h4 className="text-sm font-bold text-primary">Adaptive Lightweight Attention</h4>
                  <p className="text-[11px] text-muted-foreground">Spatial & channel feature reweighting</p>
                </div>
              </div>

              {/* Branching Outputs */}
              <div className="pt-4 border-t border-white/10">
                <span className="text-xs font-mono uppercase tracking-wider text-muted-foreground block mb-4 text-center">
                  Pipeline Execution Outputs
                </span>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Branch A: Disease Classification */}
                  <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2">
                    <div className="flex items-center gap-2 text-primary font-bold text-xs uppercase">
                      <BrainCircuit className="w-4 h-4" /> Disease Classification
                    </div>
                    <ul className="text-xs text-muted-foreground space-y-1.5 pt-1">
                      <li className="flex items-center justify-between">
                        <span>Prediction:</span>
                        <strong className="text-foreground">Disease Class Name</strong>
                      </li>
                      <li className="flex items-center justify-between">
                        <span>Confidence:</span>
                        <strong className="text-primary">Model Softmax Confidence %</strong>
                      </li>
                    </ul>
                  </div>

                  {/* Branch B: Severity Analysis */}
                  <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2">
                    <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase">
                      <Activity className="w-4 h-4" /> Severity Analysis
                    </div>
                    <ul className="text-xs text-muted-foreground space-y-1.5 pt-1">
                      <li className="flex items-center justify-between">
                        <span>Affected Area:</span>
                        <strong className="text-foreground">Estimated Leaf Area %</strong>
                      </li>
                      <li className="flex items-center justify-between">
                        <span>Category:</span>
                        <strong className="text-emerald-400">Minimal to Very Severe</strong>
                      </li>
                    </ul>
                  </div>

                  {/* Branch C: Explainable AI */}
                  <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2">
                    <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs uppercase">
                      <Eye className="w-4 h-4" /> Explainable AI (XAI)
                    </div>
                    <ul className="text-xs text-muted-foreground space-y-1.5 pt-1">
                      <li className="flex items-center justify-between">
                        <span>Attention Map:</span>
                        <strong className="text-foreground">Internal Feature Reweighting</strong>
                      </li>
                      <li className="flex items-center justify-between">
                        <span>Grad-CAM++:</span>
                        <strong className="text-cyan-400">Post-hoc 2nd-Order Heatmap</strong>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
