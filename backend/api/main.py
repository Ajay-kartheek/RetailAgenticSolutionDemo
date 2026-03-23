"""
FastAPI Main Application for SK Brands Retail AI
"""
import sys
import os

# Add backend to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import stores, products, inventory, decisions, orchestrator, campaigns, agents, activity, trends, demo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler."""
    logger.info("SK Brands Retail AI Backend starting up...")
    yield
    logger.info("SK Brands Retail AI Backend shutting down...")


app = FastAPI(
    title="SK Brands Retail AI",
    description="Agentic AI Solution for Retail Operations - Demand Forecasting, Inventory Management, Pricing, and Campaigns",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# Include routers
app.include_router(stores.router, prefix="/stores", tags=["Stores"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
app.include_router(decisions.router, prefix="/decisions", tags=["Decisions"])
app.include_router(orchestrator.router, prefix="/orchestrator", tags=["Orchestrator"])
app.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
app.include_router(agents.router) # Prefix is defined in the router itself
app.include_router(activity.router, prefix="/activity", tags=["Activity"])
app.include_router(trends.router, prefix="/trends", tags=["Trends"])
app.include_router(demo.router, prefix="/demo", tags=["Demo"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "service": "SK Brands Retail AI",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
