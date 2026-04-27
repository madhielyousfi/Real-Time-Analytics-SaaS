#!/bin/bash

# Full App Launcher - Starts both Frontend and Backend
# Usage: ./run-dev.sh

set -e

cd "$(dirname "$0")"

echo "=== Starting Backend (FastAPI on port 8001) ==="
python3 -u server.py 8001 &
BACKEND_PID=$!

echo "=== Starting Frontend (Next.js on port 3000) ==="
cd dashboard-frontend
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "=========================================="
echo "  Real-Time Analytics SaaS - Running"
echo "=========================================="
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8001"
echo ""
echo "  Backend PID:  $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop: kill $BACKEND_PID $FRONTEND_PID"
echo "=========================================="

trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

wait