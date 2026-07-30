@echo off
title AIGate — Local AI Privacy & Compliance Gateway
echo ========================================================
echo   AIGate — Local AI Privacy & Compliance Gateway v1.0
echo ========================================================
echo Avvio del microservizio backend FastAPI su 127.0.0.1:8000...
start /b python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

echo Avvio dell'interfaccia desktop frontend Next.js...
cd frontend
start /b npm run dev

echo.
echo Gateway attivo!
echo Dashboard di controllo accessibile su http://localhost:3000
echo.
