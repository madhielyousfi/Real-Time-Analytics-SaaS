#!/bin/bash
cd /home/dados/Documents/DATA\ PROECT/realtime-analytics-saas

echo "=== Starting Analytics System ==="
rm -f analytics.db
python3 -u server.py 8001 &
sleep 3

echo "=== Creating App ==="
APP=$(curl -s -X POST http://localhost:8001/api/apps -H "Content-Type: application/json" -d '{"name": "Demo App"}')
API_KEY=$(echo $APP | python3 -c "import sys,json; print(json.load(sys.stdin)['api_key'])")
SECRET=$(echo $APP | python3 -c "import sys,json; print(json.load(sys.stdin)['secret_key'])")

echo "=== Sending 20 Events ==="
for i in $(seq 1 20); do
  USER=$(( (i % 3) + 1 ))
  case $i in
    1|2|3|4|5) ET="page_view" ;;
    6|7|8|9|10) ET="click" ;;
    11|12|13|14|15) ET="signup" ;;
    *) ET="purchase" ;;
  esac
  curl -s -X POST http://localhost:8001/track \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -H "X-Secret-Key: $SECRET" \
    -d "{\"event_type\": \"$ET\", \"user_id\": \"user$USER\", \"properties\": {\"i\": $i}}" > /dev/null
done

echo ""
echo "=== Dashboard Ready ==="
echo "File: dashboard.html"
echo ""
echo "To view:"
echo "  1. Open file:///home/dados/Documents/DATA%20PROECT/realtime-analytics-saas/dashboard.html"
echo ""
echo "  Or serve locally:"
echo "  python3 -m http.server 8080 --directory ."
echo ""
echo "API Keys for testing:"
echo "  API Key: $API_KEY"
echo "  Secret Key: $SECRET"