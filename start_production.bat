@echo off
title PlantIntel AI Production Server
echo ==================================================
echo       PLANTINTEL AI - PRODUCTION LAUNCHER         
echo ==================================================
echo.

cd /d "%~dp0"

echo [1/2] Checking Frontend Production Build...
if not exist "frontend\dist\index.html" (
    echo Building frontend static bundle...
    cd frontend && npm run build && cd ..
)

echo [2/2] Starting Production Backend & Frontend Server on Port 8000...
echo Access Web Application: http://localhost:8000
echo Access API Docs:        http://localhost:8000/docs
echo.

backend\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
pause
