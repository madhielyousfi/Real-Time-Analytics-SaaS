#!/usr/bin/env python3
"""
Real-Time Analytics - SaaS-Grade Server
With: Multi-tenancy, Event Queue, Real-time Metrics, Funnels
"""
import json
import sqlite3
import uuid
import secrets
import threading
import queue
from datetime import datetime, timezone, timedelta as td
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = "./analytics.db"
EVENT_QUEUE_SIZE = 10000

app_cache = {}
metrics_cache = {}
metrics_cache_lock = threading.Lock()


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
    c.execute('''CREATE INDEX IF NOT EXISTS idx_events_app_type ON events(app_id, event_type)''')
    
    conn.commit()
    conn.close()


def get_app_by_key(api_key):
    if api_key in app_cache:
        return app_cache[api_key]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, api_key, secret_key, is_active FROM apps WHERE api_key = ?", (api_key,))
    row = c.fetchone()
    conn.close()
    
    if row:
        app = {"id": row[0], "name": row[1], "api_key": row[2], "secret_key": row[3], "is_active": row[4]}
        app_cache[api_key] = app
        return app
    return None


def verify_app_credentials(api_key, secret_key):
    app = get_app_by_key(api_key)
    if not app:
        return None
    if not secrets.compare_digest(app["secret_key"], secret_key):
        return None
    if not app["is_active"]:
        return None
    return app


def create_app(name):
    app_id = str(uuid.uuid4())
    api_key = secrets.token_urlsafe(32)
    secret_key = secrets.token_urlsafe(32)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO apps (id, name, api_key, secret_key) VALUES (?, ?, ?, ?)",
                 (app_id, name, api_key, secret_key))
        conn.commit()
        app_cache[api_key] = {"id": app_id, "name": name, "api_key": api_key, "secret_key": secret_key, "is_active": 1}
        return {"id": app_id, "name": name, "api_key": api_key, "secret_key": secret_key}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def update_metrics(app_id, event_type, user_id):
    with metrics_cache_lock:
        now = datetime.now(timezone.utc)
        minute_key = now.strftime("%Y-%m-%d %H:%M")
        
        if app_id not in metrics_cache:
            metrics_cache[app_id] = {}
        
        m = metrics_cache[app_id]
        
        m["total_events"] = m.get("total_events", 0) + 1
        
        if minute_key not in m.get("events_per_minute", {}):
            if "events_per_minute" not in m:
                m["events_per_minute"] = {}
            m["events_per_minute"][minute_key] = 0
        m["events_per_minute"][minute_key] += 1
        
        if user_id:
            if "unique_users" not in m:
                m["unique_users"] = set()
            m["unique_users"].add(user_id)
        
        if event_type not in m.get("event_types", {}):
            if "event_types" not in m:
                m["event_types"] = {}
            m["event_types"][event_type] = 0
        m["event_types"][event_type] += 1


def get_metrics(app_id):
    with metrics_cache_lock:
        if app_id not in metrics_cache:
            return {
                "total_events": 0,
                "unique_users": 0,
                "events_per_minute": {},
                "event_types": {}
            }
        
        m = metrics_cache[app_id].copy()
        if "unique_users" in m and isinstance(m["unique_users"], set):
            m["unique_users"] = len(m["unique_users"])
        return m


def get_realtime_metrics(app_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM events WHERE app_id = ?", (app_id,))
    total = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT user_id) FROM events WHERE app_id = ? AND user_id IS NOT NULL", (app_id,))
    users = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT session_id) FROM events WHERE app_id = ? AND session_id IS NOT NULL", (app_id,))
    sessions = c.fetchone()[0]
    
    c.execute("""SELECT event_type, COUNT(*) as cnt FROM events WHERE app_id = ? 
              GROUP BY event_type ORDER BY cnt DESC""", (app_id,))
    event_types = {r[0]: r[1] for r in c.fetchall()}
    
    c.execute("""SELECT strftime('%Y-%m-%d %H:', timestamp) || '00' as minute, COUNT(*) as cnt 
              FROM events WHERE app_id = ? AND timestamp >= datetime('now', '-1 hour')
              GROUP BY minute ORDER BY minute""", (app_id,))
    epm = [{"timestamp": r[0], "value": r[1]} for r in c.fetchall()]
    
    conn.close()
    
    return {
        "total_events": total,
        "unique_users": users,
        "unique_sessions": sessions,
        "event_types": event_types,
        "events_per_minute": epm
    }


def get_funnel_data(app_id, steps, start_time, end_time, window_seconds):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    step_users = {step: set() for step in steps}
    
    for step in steps:
        c.execute("""SELECT DISTINCT user_id FROM events 
              WHERE app_id = ? AND event_type = ? AND user_id IS NOT NULL
              AND timestamp BETWEEN ? AND ?""",
                  (app_id, step, start_time, end_time))
        for row in c.fetchall():
            if row[0]:
                step_users[step].add(row[0])
    
    conn.close()
    
    results = []
    prev_count = 0
    
    for i, step in enumerate(steps):
        count = len(step_users[step])
        if i == 0:
            rate = 100.0
        else:
            rate = (count / prev_count * 100) if prev_count > 0 else 0.0
        
        results.append({
            "step_name": step,
            "count": count,
            "conversion_rate": round(rate, 2)
        })
        prev_count = count
    
    overall = (results[-1]["count"] / results[0]["count"] * 100) if results[0]["count"] > 0 else 0
    
    return {
        "steps": results,
        "overall_conversion": round(overall, 2)
    }


event_queue = queue.Queue(maxsize=EVENT_QUEUE_SIZE)


def process_event_worker():
    while True:
        try:
            event = event_queue.get(timeout=1)
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            props = json.dumps(event.get("properties", {}))
            ts = event.get("timestamp", datetime.now(timezone.utc).isoformat())
            processed = datetime.now(timezone.utc).isoformat()
            
            c.execute("""INSERT INTO events (id, app_id, event_type, user_id, session_id, properties, timestamp, processed_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                     (event.get("id"), event.get("app_id"), event.get("event_type"),
                      event.get("user_id"), event.get("session_id"), props, ts, processed))
            
            conn.commit()
            conn.close()
            
            update_metrics(event.get("app_id"), event.get("event_type"), event.get("user_id"))
            
            event_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error: {e}")


class AnalyticsHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error(self, status, message):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
    
    def get_app_from_headers(self):
        api_key = self.headers.get("X-API-Key", "")
        secret_key = self.headers.get("X-Secret-Key", "")
        if not api_key or not secret_key:
            return None
        return verify_app_credentials(api_key, secret_key)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/health":
            self.send_json({"status": "healthy", "service": "analytics-saas", "queue_size": event_queue.qsize()})
        
        elif parsed.path == "/api/stats":
            app = self.get_app_from_headers()
            if not app:
                app_id = "demo"
            else:
                app_id = app["id"]
            m = get_realtime_metrics(app_id)
            self.send_json(m)
        
        elif parsed.path == "/api/metrics/summary":
            app = self.get_app_from_headers()
            if not app:
                self.send_error(401, "Authentication required")
                return
            
            m = get_realtime_metrics(app["id"])
            self.send_json({
                "app_id": app["id"],
                "app_name": app["name"],
                **m
            })
        
        elif parsed.path == "/api/apps":
            app = self.get_app_from_headers()
            if not app:
                self.send_error(401, "Auth required")
                return
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, name, api_key, is_active, created_at FROM apps")
            apps = [{"id": r[0], "name": r[1], "api_key": r[2][:8]+"...", "is_active": r[3], "created_at": r[4]} for r in c.fetchall()]
            conn.close()
            self.send_json(apps)
        
        elif parsed.path == "/api/events":
            params = parse_qs(parsed.query)
            app_id = params.get("app_id", ["demo"])[0]
            limit = min(int(params.get("limit", ["100"])[0]), 1000)
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, app_id, event_type, user_id, session_id, timestamp FROM events WHERE app_id = ? ORDER BY timestamp DESC LIMIT ?", (app_id, limit))
            events = [{"id": r[0], "app_id": r[1], "event_type": r[2], "user_id": r[3], "session_id": r[4], "timestamp": r[5]} for r in c.fetchall()]
            conn.close()
            self.send_json(events)
        
        elif parsed.path == "/api/events/recent":
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, app_id, event_type, user_id, timestamp FROM events ORDER BY timestamp DESC LIMIT 50")
            events = [{"id": r[0], "app_id": r[1], "event_type": r[2], "user_id": r[3], "timestamp": r[4]} for r in c.fetchall()]
            conn.close()
            self.send_json(events)
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        if parsed.path == "/track":
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return
            
            app = self.get_app_from_headers()
            
            if app:
                app_id = app["id"]
                app_name = app["name"]
            else:
                api_key_test = self.headers.get("X-API-Key", "")
                if api_key_test:
                    self.send_error(401, "Invalid credentials")
                    return
                app_id = data.get("app_id", "demo_app")
                app_name = "demo"
            
            if event_queue.full():
                self.send_error(503, "Queue full")
                return
            
            event_id = str(uuid.uuid4())
            ts = datetime.now(timezone.utc).isoformat()
            
            event = {
                "id": event_id,
                "app_id": app_id,
                "app_name": app_name,
                "event_type": data.get("event_type", "unknown"),
                "user_id": data.get("user_id"),
                "session_id": data.get("session_id"),
                "properties": data.get("properties", {}),
                "timestamp": data.get("timestamp") or ts,
                "received_at": ts
            }
            
            try:
                event_queue.put(event, timeout=1)
            except queue.Full:
                self.send_error(503, "Queue full")
                return
            
            self.send_json({"status": "accepted", "event_id": event_id})
        
        elif parsed.path == "/api/apps":
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return
            
            name = data.get("name")
            if not name:
                self.send_error(400, "Name required")
                return
            
            app = create_app(name)
            if not app:
                self.send_error(400, "App exists")
                return
            
            self.send_json(app, 201)
        
        elif parsed.path == "/api/funnels/query":
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return
            
            app = self.get_app_from_headers()
            if not app:
                self.send_error(401, "Auth required")
                return
            
            steps = data.get("steps", [])
            if len(steps) < 2:
                self.send_error(400, "2+ steps required")
                return
            
            start_time = data.get("start_time", (datetime.now() - td(days=7)).isoformat())
            end_time = data.get("end_time", datetime.now().isoformat())
            window = data.get("window_seconds", 86400)
            
            result = get_funnel_data(app["id"], steps, start_time, end_time, window)
            self.send_json(result)
        
        elif parsed.path == "/api/events/query":
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return
            
            app_id = data.get("app_id", "demo")
            limit = data.get("limit", 100)
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, app_id, event_type, user_id, session_id, properties, timestamp FROM events WHERE app_id = ? ORDER BY timestamp DESC LIMIT ?", (app_id, limit))
            events = [{"id": r[0], "app_id": r[1], "event_type": r[2], "user_id": r[3], "session_id": r[4], "properties": json.loads(r[5]) if r[5] else {}, "timestamp": r[6]} for r in c.fetchall()]
            conn.close()
            self.send_json(events)
        
        elif parsed.path == "/api/metrics/timeseries":
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return
            
            app = self.get_app_from_headers()
            if not app:
                self.send_error(401, "Auth required")
                return
            
            m = get_realtime_metrics(app["id"])
            self.send_json({
                "metric_name": "events",
                "data": m.get("events_per_minute", []),
                "total": m.get("total_events", 0)
            })
        
        else:
            self.send_response(404)
            self.end_headers()


def run_server(port=8001):
    init_database()
    
    threading.Thread(target=process_event_worker, daemon=True).start()
    
    server = HTTPServer(("0.0.0.0", port), AnalyticsHandler)
    print(f"=" * 60)
    print(f"Real-Time Analytics SaaS")
    print(f"Port: {port}")
    print(f"=" * 60)
    print(f"\nEndpoints:")
    print(f"  POST /track           - Track event")
    print(f"  POST /api/apps       - Create app")
    print(f"  POST /api/funnels    - Query funnels")
    print(f"  GET  /api/stats      - Get stats")
    print(f"  GET  /health        - Health")
    print(f"\nStarting...")
    server.serve_forever()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    run_server(port)