# Real-Time Analytics SaaS

[![Server Status](https://img.shields.io/badge/Server-Running-green)](http://localhost:8001)

A lightweight, end-to-end real-time analytics platform built from scratch, designed to simulate how modern product analytics tools (like PostHog or Mixpanel) work internally.

This project covers the full data lifecycle: event ingestion → processing → storage → real-time metrics → interactive dashboard.

## Running

```bash
./run.sh
```

Then open http://localhost:8001

## Features

- API Key Authentication (multi-tenant apps)
- Event Tracking API (/track)
- Asynchronous Event Queue (decoupled ingestion)
- Real-Time Metrics Engine
- Per-minute aggregation
- Funnel Analysis (conversion tracking)
- Live Dashboard (Charts + Tables)
- Multi-Application Support
- SQLite Data Warehouse

## Architecture

```
Client SDK
    ↓
POST /track (API Keys)
    ↓
Event Queue (async)
    ↓
Background Worker
    ↓
SQLite Database
    ↓
Real-Time Metrics Cache
    ↓
Dashboard (Charts + Funnel Analysis)
```

## Tech Stack

### Backend
- Python (standard library)
- Async event processing
- REST API server

### Frontend
- HTML + TailwindCSS
- Chart.js (data visualization)

### Data Layer
- SQLite (event storage)
- In-memory cache (real-time metrics)

## Getting Started

```bash
git clone https://github.com/madhielyousfi/Real-Time-Analytics-SaaS.git
cd Real-Time-Analytics-SaaS
chmod +x run.sh
./run.sh
```

Access everything at: **http://localhost:8001**

## Example API Usage

```bash
curl -X POST http://localhost:8001/track \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "X-Secret-Key: YOUR_SECRET" \
  -d '{
    "event_type": "page_view",
    "user_id": "user_1",
    "properties": {
      "page": "/home"
    }
  }'
```

## Example Metrics

- Total Events
- Unique Users
- Sessions
- Events per Minute
- Event Distribution
- Funnel Conversion Rates

## Project Goals

This project was built to:

- Understand real-time data pipelines
- Practice backend system design
- Simulate SaaS analytics architecture
- Build a full-stack data product from scratch

## Future Improvements

- Next.js dashboard (modern UI)
- User authentication system
- WebSocket real-time updates
- Advanced analytics (retention, cohorts)
- PostgreSQL + Redis integration
- Cloud deployment (Docker + CI/CD)

## Why This Project Matters

Most tutorials stop at data processing. This project goes further by building a complete analytics product, similar to real-world systems used in production.