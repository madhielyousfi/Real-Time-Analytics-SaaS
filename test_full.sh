#!/bin/bash
cd /home/dados/Documents/DATA\ PROECT/realtime-analytics-saas
pkill -f server.py 2>/dev/null
sleep 1
rm -f analytics.db
python3 -u server.py 8001 &
sleep 3

echo "=== Create App ==="
curl -s -X POST http://localhost:8001/api/apps -H "Content-Type: application/json" -d '{"name": "testapp"}'
echo ""

echo "=== Get API Keys ==="
API_KEY=$(sqlite3 analytics.db "SELECT api_key FROM apps LIMIT 1")
SECRET=$(sqlite3 analytics.db "SELECT secret_key FROM apps LIMIT 1")
echo "KEY: $API_KEY"

echo "=== Track Events ==="
curl -s -X POST http://localhost:8001/track -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Secret-Key: $SECRET" -d '{"event_type": "page_view", "user_id": "u1"}'
curl -s -X POST http://localhost:8001/track -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Secret-Key: $SECRET" -d '{"event_type": "page_view", "user_id": "u2"}'
curl -s -X POST http://localhost:8001/track -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Secret-Key: $SECRET" -d '{"event_type": "signup", "user_id": "u1"}'
curl -s -X POST http://localhost:8001/track -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Secret-Key: $SECRET" -d '{"event_type": "purchase", "user_id": "u1"}'

echo ""
echo "=== Send More Events ==="
for i in 3 4 5; do
  curl -s -X POST http://localhost:8001/track -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Secret-Key: $SECRET" -d "{\"event_type\": \"click\", \"user_id\": \"u$i\"}"
done

sleep 1

echo "=== Get Stats ==="
curl -s http://localhost:8001/api/stats -H "X-API-Key: $API_KEY" -H "X-Secret-Key: $SECRET"
echo ""

echo "=== Funnel Query ==="
curl -s -X POST http://localhost:8001/api/funnels/query -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Secret-Key: $SECRET" -d '{"steps": ["page_view", "signup", "purchase"]}'
echo ""

echo "=== DONE ==="