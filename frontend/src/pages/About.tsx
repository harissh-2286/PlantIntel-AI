import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function About() {
  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      <div className="text-center">
        <h1 className="text-3xl font-bold tracking-tight">PlantIntel AI</h1>
        <p className="text-muted-foreground mt-2">Deep Learning Capstone Project</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Technology Stack</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span> EfficientNetV2-S
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-500"></span> Adaptive Lightweight Attention
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-500"></span> Grad-CAM++
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500"></span> Severity Analysis
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
