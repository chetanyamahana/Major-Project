import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# API settings
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "Grievance Redressal System"
PROJECT_DESCRIPTION = "A system for collecting and analyzing civic grievances"
PROJECT_VERSION = "0.1.0"

# Google Sheets settings
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEETS_TOKEN_FILE = os.getenv("GOOGLE_SHEETS_TOKEN_FILE", "token.json")
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")

# Twitter API settings
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Scraping settings
SCRAPING_USER_AGENT = "GrievanceRedressalBot/1.0"
SCRAPING_REQUEST_TIMEOUT = 30  # seconds

# Municipalities and government portals to scrape
MUNICIPALITY_PORTALS = [
    {
        "name": "Municipal Corporation of Delhi",
        "url": "https://mcdonline.nic.in/grievanceredressal/",
        "type": "municipality"
    },
    {
        "name": "Swachh Bharat Mission",
        "url": "https://swachhbharat.mygov.in/",
        "type": "government"
    },
    {
        "name": "Chandigarh Municipal Corporation",
        "url": "https://mcchandigarh.gov.in/complaints",
        "type": "municipality"
    }
]

# Twitter search queries
TWITTER_SEARCH_QUERIES = [
    "pothole complaint",
    "garbage disposal problem",
    "street light not working",
    "water supply issue",
    "sewage problem",
    "municipal corporation"
]
