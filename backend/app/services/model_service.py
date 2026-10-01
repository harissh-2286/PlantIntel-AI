from fastapi import UploadFile
import asyncio
from app.schemas.response import AnalysisResponse

class ModelService:
    def __init__(self):
        # Initialize actual model here when available
        self.is_demo_mode = True

    async def analyze(self, file: UploadFile) -> AnalysisResponse:
        # Simulate processing delay
        await asyncio.sleep(2)
        
        # In a real scenario, we would process the image through the PyTorch model
        # return await self._real_analysis(file)
        
        return self._demo_analysis()

    def _demo_analysis(self) -> AnalysisResponse:
        return AnalysisResponse(
            mode="demo",
            prediction={
                "class_name": "Tomato Late Blight",
                "confidence": 0.964
            },
            top_predictions=[
                {"class_name": "Tomato Late Blight", "confidence": 0.964},
                {"class_name": "Tomato Early Blight", "confidence": 0.021},
                {"class_name": "Tomato Septoria Leaf Spot", "confidence": 0.008},
                {"class_name": "Tomato Leaf Mold", "confidence": 0.004},
                {"class_name": "Healthy Leaf", "confidence": 0.003},
            ],
            severity={
                "label": "Moderate",
                "affected_area": 0.287
            },
            explainability={
                "gradcam": "demo_gradcam_url",
                "attention_map": "demo_attention_url",
                "segmentation": "demo_segmentation_url",
                "iou": 0.71,
                "dice": 0.68
            },
            model={
                "name": "EfficientNetV2-S + Adaptive Lightweight Attention",
                "version": "v1.0-demo"
            }
        )
