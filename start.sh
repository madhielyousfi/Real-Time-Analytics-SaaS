#!/bin/bash
# Simple launcher - starts services and opens browser
cd /home/dados/Documents/DATA\ PROECT/realtime-analytics-saas

echo "Starting Real-Time Analytics SaaS..."

# Kill existing
pkill -f "server.py" 2>/dev/null
pkill -f "http.server" 2>/dev/null
sleep 1

# Clean
rm -f analytics.db .api_keys

# Start backend
python3 server.py 8001 &
BACKEND=$!

# Start dashboard  
python3 -m http.server 9999 &
DASHBOARD=$!

sleep 4

# Create demo app
APP=$(curl -s -X POST http://localhost:8001/api/apps -H "Content-Type: application/json" -d '{"name": "Demo"}')
API_KEY=$(echo $APP | python3 -c "import sys,json; print(json.load(sys.stdin)['api_key'])" 2>/dev/null)
SECRET=$(echo $APP | python3 -c "import sys,json; print(json.load(sys.stdin)['secret_key'])" 2>/dev/null)

# Send events
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25; do
  USER=$((i % 5 + 1))
  if [ $i -le 10 ]; then ET="page_view"
  elif [ $i -le 17 ]; then ET="click"
  elif [ $i -le 20 ]; then ET="signup"
  else ET="purchase"
  fi
  curl -s -X POST http://localhost:8001/track \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -H "X-Secret-Key: $SECRET" \
    -d "{\"event_type\": \"$ET\", \"user_id\": \"user$USER\"}" >/dev/null
done

echo ""
echo "=========================================="
echo "  Ready!"
echo "=========================================="
echo ""
echo "  Backend:   http://localhost:8001"
echo "  Dashboard: http://localhost:9999/dashboard.html"
echo ""
echo "Opening Firefox..."
firefox http://localhost:9999/dashboard.html 2>/dev/null

echo ""
echo "Services running. Press Ctrl+C to stop."
echo ""

# Wait
wait