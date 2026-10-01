import { Card, CardContent } from "@/components/ui/card"

export default function PlantCare() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Plant Care Guide</h1>
        <p className="text-muted-foreground mt-2">General guidance based on AI analysis.</p>
      </div>
      
      <Card>
        <CardContent className="pt-6">
          <p className="mb-4">This application is intended for AI-assisted plant disease analysis.</p>
          <p className="text-sm text-muted-foreground">
            Disclaimer: The results provided by the AI model are for informational purposes only. Do not rely on them as professional agricultural treatment advice. Consult with an expert before applying any chemicals or drastic treatments.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
