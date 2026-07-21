# app/api/v1/sync.py

import logging
from fastapi import APIRouter, BackgroundTasks

from app.scripts.sync_gdrive import run_sync 

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sync"])

def _sync_task():
    """Background task to run the sync."""
    logger.info("Manual sync triggered.")
    run_sync()
    logger.info("Manual sync completed.")

@router.post("/sync")
async def trigger_sync(background_tasks: BackgroundTasks):
    """Trigger a manual sync of Google Drive documents."""
    background_tasks.add_task(_sync_task)
    return {"status": "sync_started", "message": "Sync is running in the background."}