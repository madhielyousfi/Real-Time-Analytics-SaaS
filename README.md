# Real-Time Analytics SaaS

A production-grade monorepo for real-time analytics with Kafka, FastAPI, and a modern dashboard.

## Architecture

```
Client SDK → Ingestion Service → Kafka → Stream Processor → PostgreSQL → Backend API → Dashboard
```

## Services

- **ingestion-service**: High-throughput event ingestion API
- **backend**: Core API (auth, apps, users, analytics)
- **stream-processor**: Real-time event processing engine
- **worker**: Background jobs (recompute, cleanup)
- **dashboard-frontend**: React/Next.js analytics dashboard

## Quick Start

```bash
docker-compose up -d
```

## Environment

See `.env.example` for required environment variables.

## License

MIT