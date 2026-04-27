#!/usr/bin/env python3
import json
import sqlite3
import time
import sys
import os
from datetime import datetime, timezone
import threading

sys.path.insert(0, "/home/dados/Documents/DATA PROECT/realtime-analytics-saas/ingestion-service")

DB_PATH = "/home/dados/Documents/DATA PROECT/realtime-analytics-saas/analytics.db"

import simple_server

events_store = simple_server.events_store
db_lock = simple_server.db_lock


def process_event(event_data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    props = json.dumps(event_data.get("properties", {}))
    ts = event_data.get("timestamp", datetime.now(timezone.utc).isoformat())
    processed = datetime.now(timezone.utc).isoformat()
    
    c.execute("""INSERT OR REPLACE INTO events (id, app_id, event_type, user_id, session_id, properties, timestamp, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
             (event_data.get("id"), event_data.get("app_id"), event_data.get("event_type"),
              event_data.get("user_id"), event_data.get("session_id"), props, ts, processed))
    
    conn.commit()
    conn.close()


def start_processor():
    print("Stream processor started - processing events...")
    last_count = 0
    
    while True:
        with db_lock:
            current_count = len(events_store)
        
        if current_count > last_count:
            with db_lock:
                new_events = list(events_store[last_count:current_count])
        
            for event in new_events:
                try:
                    process_event(event)
                    print(f"Processed: {event['event_type']} for {event['app_id']}")
                except Exception as e:
                    print(f"Error: {e}")
        
        last_count = current_count
        time.sleep(0.5)


if __name__ == "__main__":
    start_processor()