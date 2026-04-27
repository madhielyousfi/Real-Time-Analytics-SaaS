#!/bin/bash
cd /home/dados/Documents/DATA\ PROECT/realtime-analytics-saas

kill_port() {
    lsof -ti:$1 | xargs -r kill -9 2>/dev/null
}

kill_port 8001
sleep 1

rm -f analytics.db

echo "Starting server..."
python3 -u server.py 8001 &
sleep 3

echo ""
echo "=== TESTING ==="
echo "1. Health check:"
curl -s http://localhost:8001/health
echo ""

echo ""
echo "2. Create app 'myapp':"
curl -s -X POST http://localhost:8001/api/apps -H "Content-Type: application/json" -d '{"name": "myapp"}'
echo ""

sleep 1

echo ""
echo "3. Track events with API key:"
API_KEY=$(sqlite3 analytics.db "SELECT api_key FROM apps LIMIT 1")
SECRET_KEY=$(sqlite3 analytics.db "SELECT secret_key FROM apps LIMIT 1")

echo "API Key: $API_KEY"
echo "Secret Key: $SECRET_KEY"

curl -s -X POST http://localhost:8001/track \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -H "X-Secret-Key: $SECRET_KEY" \
  -d '{"event_type": "page_view", "user_id": "user1"}'

echo ""

curl -s -X POST http://localhost:8001/track \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -H "X-Secret-Key: $SECRET_KEY" \
  -d '{"event_type": "click", "user_id": "user1"}'

echo ""

sleep 2

echo ""
echo "4. Get stats:"
curl -s http://localhost:8001/api/stats \
  -H "X-API-Key: $API_KEY" \
  -H "X-Secret-Key: $SECRET_KEY"
echo ""

echo ""
echo "5. Get metrics summary:"
curl -s http://localhost:8001/api/metrics/summary \
  -H "X-API-Key: $API_KEY" \
  -H "X-Secret-Key: $SECRET_KEY"
echo ""

echo ""
echo "=== DONE ==="