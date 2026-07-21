# backend/app/api/router.py

from fastapi import APIRouter

from app.api.v1 import chat, health, sync

# Create the main API router
api_router = APIRouter()

# Include v1 routes
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(sync.router)