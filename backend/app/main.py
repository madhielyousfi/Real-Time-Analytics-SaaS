from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_db
from .api.routes import auth, apps, events, metrics, funnels

settings = get_settings()

app = FastAPI(
    title="Real-Time Analytics API",
    description="Backend API for real-time analytics platform",
    version="1.0.0"
)

origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(auth.router, prefix="/api")
app.include_router(apps.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(funnels.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)