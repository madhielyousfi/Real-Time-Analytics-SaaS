#!/bin/bash

cd /home/dados/Documents/DATA\ PROECT/realtime-analytics-saas

rm -f analytics.db

echo "Starting Real-Time Analytics SaaS on http://localhost:8001"

python3 server.py 8001