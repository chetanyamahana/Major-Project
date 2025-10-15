from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional
import uuid
import asyncio

from app.models.grievance import GrievanceCreate, GrievanceResponse, GrievanceList, GrievanceStats
from app.db.google_sheets import GoogleSheetsDB
from app.scrapers.scraper_manager import ScraperManager

# Create router
router = APIRouter()

# Initialize database
db = GoogleSheetsDB()

# Initialize scraper manager
scraper_manager = ScraperManager()

@router.post("/grievances/", response_model=GrievanceResponse, status_code=201)
async def create_grievance(grievance: GrievanceCreate):
    """
    Create a new grievance.
    """
    # Generate ticket ID
    ticket_id = f"CS{uuid.uuid4().hex[:8].upper()}"
    
    # Store in database
    db_grievance = db.create_grievance(grievance, ticket_id)
    
    return db_grievance

@router.get("/grievances/", response_model=GrievanceList)
async def get_grievances(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100)):
    """
    Get a list of grievances with pagination.
    """
    grievances = db.get_grievances(skip, limit)
    total = len(db.get_grievances(0, 1000))  # Approximate total count
    
    return {
        "items": grievances,
        "total": total
    }

@router.get("/grievances/{ticket_id}", response_model=GrievanceResponse)
async def get_grievance(ticket_id: str):
    """
    Get a specific grievance by ticket ID.
    """
    grievance = db.get_grievance_by_id(ticket_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    
    return grievance

@router.patch("/grievances/{ticket_id}/status")
async def update_grievance_status(ticket_id: str, resolved: bool):
    """
    Update the resolved status of a grievance.
    """
    grievance = db.update_grievance_status(ticket_id, resolved)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")
    
    return {"message": "Status updated successfully", "grievance": grievance}

@router.get("/stats/", response_model=GrievanceStats)
async def get_statistics():
    """
    Get statistics about grievances.
    """
    stats = db.get_grievance_stats()
    return stats

@router.post("/scrape/")
async def trigger_scraping(background_tasks: BackgroundTasks):
    """
    Trigger scraping of all sources.
    """
    # Run in background
    background_tasks.add_task(scraper_manager.run_all_scrapers)
    
    return {"message": "Scraping started in background"}

@router.post("/scrape/{source}")
async def trigger_source_scraping(source: str, background_tasks: BackgroundTasks):
    """
    Trigger scraping of a specific source.
    """
    # Run in background
    background_tasks.add_task(scraper_manager.run_scraper, source)
    
    return {"message": f"Scraping of {source} started in background"}
