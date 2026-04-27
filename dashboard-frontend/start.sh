#!/bin/bash
cd "/home/dados/Documents/DATA PROECT/realtime-analytics-saas"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

echo "=== Starting Backend ==="
python3 -u server.py 8001 &
BACKEND_PID=$!

echo "=== Starting Frontend ==="
cd dashboard-frontend
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "=== Ready ==="
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8001"
echo ""
echo "To stop:"
echo "  kill $BACKEND_PID $FRONTEND_PID"

wait