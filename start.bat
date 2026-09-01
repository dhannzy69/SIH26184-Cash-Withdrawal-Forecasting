@echo off
title SIH26184 Cybercrime Forecasting Platform Launcher
echo ======================================================================
echo Starting SIH26184: Cybercrime Cash-Withdrawal Location Forecaster
echo Theme: Blockchain and Cybersecurity ^| Team: Apex Pointers
echo ======================================================================
echo.

echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "SIH26184 Backend" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo [2/2] Launching React + Vite Frontend on http://127.0.0.1:5173 ...
start "SIH26184 Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ======================================================================
echo Servers successfully launched!
echo - Frontend Portal: http://127.0.0.1:5173
echo - Backend API Docs: http://127.0.0.1:8000/docs
echo ======================================================================
pause
