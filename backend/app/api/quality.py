from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.image_quality import analyze_image_quality
from app.schemas.quality import QualityResponse

router = APIRouter()

@router.post("/quality-check", response_model=QualityResponse)
async def quality_check(file: UploadFile = File(...)):
        
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not read uploaded file.")
        
    # Check max file size (10 MB limit)
    MAX_SIZE = 10 * 1024 * 1024
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
    response = analyze_image_quality(contents, file.filename)
    return response
