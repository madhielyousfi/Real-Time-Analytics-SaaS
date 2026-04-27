#!/usr/bin/env python3
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

DB_PATH = "./analytics.db"
db_lock = threading.Lock()


def init_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS apps (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        api_key TEXT NOT NULL UNIQUE,
        secret_key TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        app_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        user_id TEXT,
        session_id TEXT,
        properties TEXT,
        timestamp TEXT NOT NULL,
        processed_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE INDEX IF NOT EXISTS idx_events_app_id ON events(app_id)''')
    c.execute('''CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)''')
    c.execute('''CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id)''')
    c.execute('''CREATE INDEX IF NOT EXISTS idx_events_session_id ON events(session_id)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        app_id TEXT NOT NULL,
        user_id TEXT,
        session_id TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT,
        duration_seconds INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()
    print("Database initialized")


init_database()


class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/health":
            self.send_json({"status": "healthy"})
        
        elif parsed.path == "/api/health":
            self.send_json({"status": "healthy"})
        
        elif parsed.path == "/api/stats":
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            c.execute("SELECT COUNT(*) FROM events")
            total_events = c.fetchone()[0]
            
            c.execute("SELECT COUNT(DISTINCT user_id) FROM events WHERE user_id IS NOT NULL")
            unique_users = c.fetchone()[0]
            
            c.execute("SELECT COUNT(DISTINCT session_id) FROM events WHERE session_id IS NOT NULL")
            unique_sessions = c.fetchone()[0]
            
            conn.close()
            
            self.send_json({
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_sessions": unique_sessions
            })
        
        elif parsed.path == "/api/metrics/summary":
            params = parse_qs(parsed.query)
            app_id = params.get("app_id", ["demo_app"])[0]
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            c.execute("SELECT COUNT(*) FROM events WHERE app_id = ?", (app_id,))
            total_events = c.fetchone()[0]
            
            c.execute("SELECT COUNT(DISTINCT user_id) FROM events WHERE app_id = ? AND user_id IS NOT NULL", (app_id,))
            unique_users = c.fetchone()[0]
            
            c.execute("SELECT COUNT(DISTINCT session_id) FROM events WHERE app_id = ? AND session_id IS NOT NULL", (app_id,))
            unique_sessions = c.fetchone()[0]
            
            conn.close()
            
            self.send_json({
                "app_id": app_id,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_sessions": unique_sessions,
                "avg_session_duration_seconds": 0
            })
        
        elif parsed.path == "/api/events":
            params = parse_qs(parsed.query)
            app_id = params.get("app_id", ["demo_app"])[0]
            limit = int(params.get("limit", ["100"])[0])
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            c.execute("SELECT id, app_id, event_type, user_id, session_id, timestamp FROM events WHERE app_id = ? ORDER BY timestamp DESC LIMIT ?", 
                    (app_id, limit))
            events = []
            for row in c.fetchall():
                events.append({
                    "id": row[0],
                    "app_id": row[1],
                    "event_type": row[2],
                    "user_id": row[3],
                    "session_id": row[4],
                    "timestamp": row[5]
                })
            
            conn.close()
            self.send_json(events)
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        if parsed.path == "/api/events/query":
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                self.send_error(400)
                return
            
            app_id = data.get("app_id", "demo_app")
            limit = data.get("limit", 100)
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            c.execute("SELECT id, app_id, event_type, user_id, session_id, properties, timestamp FROM events WHERE app_id = ? ORDER BY timestamp DESC LIMIT ?", 
                    (app_id, limit))
            events = []
            for row in c.fetchall():
                events.append({
                    "id": row[0],
                    "app_id": row[1],
                    "event_type": row[2],
                    "user_id": row[3],
                    "session_id": row[4],
                    "properties": json.loads(row[5]) if row[5] else {},
                    "timestamp": row[6]
                })
            
            conn.close()
            self.send_json(events)
        
        elif parsed.path == "/api/metrics/timeseries":
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                self.send_error(400)
                return
            
            app_id = data.get("app_id", "demo_app")
            start_time = data.get("start_time", (datetime.now() - timedelta(days=7)).isoformat())
            end_time = data.get("end_time", datetime.now().isoformat())
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            c.execute("""SELECT timestamp, COUNT(*) as count FROM events 
                    WHERE app_id = ? AND timestamp >= ? AND timestamp <= ?
                    GROUP BY date(timestamp) ORDER BY timestamp""", 
                    (app_id, start_time, end_time))
            
            data_points = []
            for row in c.fetchall():
                data_points.append({
                    "timestamp": row[0],
                    "value": row[1]
                })
            
            conn.close()
            self.send_json({
                "metric_name": "events",
                "data": data_points,
                "total": sum(d["value"] for d in data_points)
            })
        
        else:
            self.send_error(404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error(self, status):
        self.send_response(status)
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


def start_server(port=8000):
    server = HTTPServer(("0.0.0.0", port), APIHandler)
    print(f"Backend API running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    start_server()