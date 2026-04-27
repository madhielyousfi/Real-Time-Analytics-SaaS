#!/usr/bin/env python3
import json
import uuid
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

events_store = []
event_handlers = []
db_lock = threading.Lock()


def register_handler(handler):
    event_handlers.append(handler)


class EventHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == "/track" or self.path == "/api/track":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            try:
                event_data = json.loads(body.decode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            
            api_key = self.headers.get("X-API-Key", "")
            secret_key = self.headers.get("X-Secret-Key", "")
            
            if api_key and secret_key:
                app_id = f"{api_key[:8]}_{secret_key[:8]}"
            else:
                app_id = event_data.get("app_id", "demo_app")
            
            event_data["app_id"] = app_id
            event_data["id"] = str(uuid.uuid4())
            event_data["received_at"] = datetime.now(timezone.utc).isoformat()
            
            if not event_data.get("timestamp"):
                event_data["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            with db_lock:
                events_store.append(event_data)
            
            for handler in event_handlers:
                handler(event_data)
            
            if not event_handlers:
                print(f"Event stored: {event_data['event_type']} for {app_id}")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "accepted", "event_id": event_data["id"]}).encode())
        
        elif self.path == "/track/batch" or self.path == "/api/track/batch":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            try:
                payload = json.loads(body.decode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return
            
            events = payload.get("events", [])
            api_key = self.headers.get("X-API-Key", "")
            secret_key = self.headers.get("X-Secret-Key", "")
            
            if api_key and secret_key:
                app_id = f"{api_key[:8]}_{secret_key[:8]}"
            else:
                app_id = "demo_app"
            
            stored = []
            with db_lock:
                for event in events:
                    event["app_id"] = app_id
                    event["id"] = str(uuid.uuid4())
                    event["timestamp"] = event.get("timestamp") or datetime.now(timezone.utc).isoformat()
                    event["received_at"] = datetime.now(timezone.utc).isoformat()
                    events_store.append(event)
                    stored.append(event["id"])
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "total": len(events),
                "accepted": len(stored)
            }).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


def get_events(app_id=None, limit=100):
    with db_lock:
        if app_id:
            filtered = [e for e in events_store if e.get("app_id") == app_id]
            return filtered[-limit:]
        return events_store[-limit:]


def get_events_count(app_id=None):
    with db_lock:
        if app_id:
            return len([e for e in events_store if e.get("app_id") == app_id])
        return len(events_store)


def clear_events():
    global events_store
    with db_lock:
        events_store = []


def start_server(port=8001):
    server = HTTPServer(("0.0.0.0", port), EventHandler)
    print(f"Ingestion service running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    start_server()