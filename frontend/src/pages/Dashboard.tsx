import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Activity, Brain, Target } from "lucide-react"

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          Research Dashboard 
          <span className="px-3 py-1 rounded-full bg-warning/20 text-warning text-xs font-bold uppercase tracking-wider">Demo Mode</span>
        </h1>
        <p className="text-muted-foreground mt-2">Model performance metrics and architecture details.</p>
      </div>
      
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary/10 text-primary rounded-lg">
                <Target className="w-5 h-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Accuracy</p>
                <h3 className="text-2xl font-bold">98.2%</h3>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-secondary/10 text-secondary rounded-lg">
                <BarChart className="w-5 h-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">F1 Score</p>
                <h3 className="text-2xl font-bold">0.981</h3>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-accent/10 text-accent rounded-lg">
                <Brain className="w-5 h-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">XAI IoU</p>
                <h3 className="text-2xl font-bold">0.76</h3>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-warning/10 text-warning rounded-lg">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Inference</p>
                <h3 className="text-2xl font-bold">45ms</h3>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Architecture Details</CardTitle>
        </CardHeader>
        <CardContent>
           <div className="overflow-x-auto">
             <table className="w-full text-sm text-left">
               <thead className="text-xs uppercase bg-white/5 text-muted-foreground">
                 <tr>
                   <th className="px-6 py-3 rounded-tl-lg">Model</th>
                   <th className="px-6 py-3">Parameters</th>
                   <th className="px-6 py-3">Accuracy</th>
                   <th className="px-6 py-3">F1 Score</th>
                   <th className="px-6 py-3 rounded-tr-lg">Notes</th>
                 </tr>
               </thead>
               <tbody>
                 <tr className="border-b border-white/5">
                   <td className="px-6 py-4 font-medium">EfficientNetV2-S (Baseline)</td>
                   <td className="px-6 py-4">22M</td>
                   <td className="px-6 py-4">95.4%</td>
                   <td className="px-6 py-4">0.950</td>
                   <td className="px-6 py-4 text-muted-foreground">Standard fine-tuning</td>
                 </tr>
                 <tr className="bg-primary/5 text-primary border-b border-white/5">
                   <td className="px-6 py-4 font-medium flex items-center gap-2">
                     <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
                     EfficientNetV2-S + Adaptive Attention
                   </td>
                   <td className="px-6 py-4">24M</td>
                   <td className="px-6 py-4 font-bold">98.2%</td>
                   <td className="px-6 py-4 font-bold">0.981</td>
                   <td className="px-6 py-4 text-primary/70">Production model</td>
                 </tr>
               </tbody>
             </table>
           </div>
        </CardContent>
      </Card>
    </div>
  )
}
