#!/bin/bash
cd /home/dados/Documents/DATA\ PROECT/realtime-analytics-saas

# Kill existing servers
pkill -f "server.py" 2>/dev/null
sleep 1

# Clean start
rm -f analytics.db

echo "Starting server..."
python3 -u server.py 8001 &
sleep 3

# Create app and get keys in one call
APP=$(curl -s -X POST http://localhost:8001/api/apps -H "Content-Type: application/json" -d '{"name": "testapp"}')
echo "App: $APP"

API_KEY=$(echo $APP | python3 -c "import sys,json; print(json.load(sys.stdin)['api_key'])")
SECRET=$(echo $APP | python3 -c "import sys,json; print(json.load(sys.stdin)['secret_key'])")

echo "API Key: ${API_KEY:0:20}..."

# Send events
echo "Sending events..."
for et in page_view page_view signup click purchase; do
  curl -s -X POST http://localhost:8001/track \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -H "X-Secret-Key: $SECRET" \
    -d "{\"event_type\": \"$et\", \"user_id\": \"user1\"}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"  {d.get('status')}\")"
done

sleep 1

echo ""
echo "=== STATS ==="
curl -s http://localhost:8001/api/stats \
  -H "X-API-Key: $API_KEY" \
  -H "X-Secret-Key: $SECRET"

echo ""
echo "=== METRICS ==="
curl -s http://localhost:8001/api/metrics/summary \
  -H "X-API-Key: $API_KEY" \
  -H "X-Secret-Key: $SECRET"

echo ""
echo "=== FUNNEL ==="
curl -s -X POST http://localhost:8001/api/funnels/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -H "X-Secret-Key: $SECRET" \
  -d '{"steps": ["page_view", "signup", "purchase"]}'

echo ""
echo ""
echo "=== DONE ==="