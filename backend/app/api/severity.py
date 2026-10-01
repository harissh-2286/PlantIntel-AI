from fastapi import APIRouter, File, UploadFile, HTTPException
from app.ml.severity import estimate_disease_severity

router = APIRouter()

@router.post("/severity")
async def analyze_severity(file: UploadFile = File(...)):
    try:
        contents = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read uploaded image file.")

    MAX_SIZE = 10 * 1024 * 1024
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    try:
        result = estimate_disease_severity(contents)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Severity estimation failed: {str(e)}")
