#!/usr/bin/env python3
import subprocess
import sys
import time
import threading
import os

os.chdir("/home/dados/Documents/DATA PROECT/realtime-analytics-saas")

services = []


def run_service(script_path, name, port=None):
    print(f"Starting {name}...")
    try:
        proc = subprocess.Popen([sys.executable, script_path], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.STDOUT)
        services.append((name, proc))
        if port:
            print(f"{name} starting on port {port}")
        time.sleep(1)
    except Exception as e:
        print(f"Error starting {name}: {e}")


print("=" * 50)
print("Starting Real-Time Analytics System")
print("=" * 50)

print("\n1. Starting Stream Processor...")
subprocess.Popen([sys.executable, "/home/dados/Documents/DATA PROECT/realtime-analytics-saas/stream-processor/simple_processor.py"])

time.sleep(2)

print("\n2. Starting Backend API on port 8000...")
subprocess.Popen([sys.executable, "/home/dados/Documents/DATA PROECT/realtime-analytics-saas/backend/simple_server.py"])

time.sleep(1)

print("\n3. Starting Ingestion Service on port 8001...")
subprocess.Popen([sys.executable, "/home/dados/Documents/DATA PROECT/realtime-analytics-saas/ingestion-service/simple_server.py"])

time.sleep(2)

print("\n" + "=" * 50)
print("System Started!")
print("=" * 50)

print("\nEndpoints:")
print("  - Ingestion: http://localhost:8001/track")
print("  - Backend API: http://localhost:8000/api/stats")
print("  - Health: http://localhost:8001/health")

print("\nTesting...")

import urllib.request
import urllib.error

try:
    resp = urllib.request.urlopen("http://localhost:8001/health")
    print(f"  Ingestion: {resp.status}")
except Exception as e:
    print(f"  Ingestion: {e}")

try:
    resp = urllib.request.urlopen("http://localhost:8000/health")
    print(f"  Backend: {resp.status}")
except Exception as e:
    print(f"  Backend: {e}")

print("\n" + "=" * 50)
print("Ready to accept events!")
print("=" * 50)