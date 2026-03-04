"""
Main entry point for the ER Recommender System API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager

# Import routers
from app.api import health, recommend, hospitals, forecasts, feedback, dashboard, geocode
from app.core import config, logging, security
from app.core.logging import logger

logging.setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start APScheduler only in non-production environments
    scheduler = None
    if os.getenv("ENVIRONMENT", "dev") != "prod":
        from app import scheduler as s
        scheduler = s.start()
    else:
        logger.info("Production environment - skipping APScheduler startup (jobs handled by Azure Container App Job)")
    
    yield
    if scheduler:
        scheduler.shutdown()
        logger.info("APScheduler shutdown")

app = FastAPI(
    title="ER Recommender System API",
    description="API for recommending emergency room facilities based on congestion and proximity",
    version="1.1.1",
    lifespan=lifespan,
)

# Security headers
app.add_middleware(security.SecurityHeadersMiddleware)

# Configure CORS - use environment variable for allowed origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(recommend.router, prefix="/api")
app.include_router(hospitals.router, prefix="/api")
app.include_router(forecasts.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(geocode.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return { 
        "message": "ER Recommender System API",
        "version": "1.1.1",
        "status": "running"
    }
