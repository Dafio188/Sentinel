#!/bin/bash
echo "========================================================"
echo "  AIGate — Local AI Privacy & Compliance Gateway v1.0"
echo "========================================================"
echo "Avvio del microservizio backend FastAPI su 127.0.0.1:8000..."
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "Avvio dell'interfaccia desktop frontend Next.js..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "Gateway attivo!"
echo "Dashboard di controllo accessibile su http://localhost:3000"
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
