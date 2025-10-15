from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.config.settings import PROJECT_NAME, PROJECT_DESCRIPTION, PROJECT_VERSION, API_V1_PREFIX, BASE_DIR
from app.api.endpoints import router as api_router

# Create FastAPI app
app = FastAPI(
    title=PROJECT_NAME,
    description=PROJECT_DESCRIPTION,
    version=PROJECT_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=API_V1_PREFIX)

# Set up templates
templates = Jinja2Templates(directory=str(BASE_DIR))

# Mount static files if directory exists
static_dir = BASE_DIR / "static"
if not static_dir.exists():
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Serve the main HTML page.
    """
    return templates.TemplateResponse("upload_page.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Serve the dashboard HTML page.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/sheets-dashboard", response_class=HTMLResponse)
async def sheets_dashboard(request: Request):
    """
    Serve the Google Sheets dashboard HTML page.
    """
    return templates.TemplateResponse("sheets_dashboard.html", {"request": request})

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
