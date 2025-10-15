import asyncio
import logging
from typing import List, Dict, Any
import uuid

from app.scrapers.base_scraper import BaseScraper
from app.scrapers.municipality_scraper import MunicipalityScraper
from app.scrapers.twitter_scraper import TwitterScraper
from app.config.settings import MUNICIPALITY_PORTALS
from app.db.google_sheets import GoogleSheetsDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ScraperManager:
    """
    Manager for all scrapers. Coordinates scraping and data storage.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("scraper.manager")
        self.scrapers: List[BaseScraper] = []
        try:
            self.db = GoogleSheetsDB()
            self._initialize_scrapers()
        except Exception as e:
            self.logger.error(f"Failed to initialize scraper manager: {e}")
            self.db = GoogleSheetsDB()  # Will use mock database
        
    def _initialize_scrapers(self):
        """
        Initialize all scrapers.
        """
        # Add municipality scrapers
        for portal in MUNICIPALITY_PORTALS:
            self.scrapers.append(MunicipalityScraper(portal["name"], portal["url"]))
        
        # Add Twitter scraper
        self.scrapers.append(TwitterScraper())
        
        self.logger.info(f"Initialized {len(self.scrapers)} scrapers")
    
    async def run_all_scrapers(self) -> int:
        """
        Run all scrapers and store results.
        Returns the number of new grievances found.
        """
        self.logger.info("Starting scraper run")
        
        if not self.scrapers:
            self.logger.warning("No scrapers initialized. Attempting to initialize now.")
            try:
                self._initialize_scrapers()
            except Exception as e:
                self.logger.error(f"Failed to initialize scrapers: {e}")
                return 0
                
        if not self.scrapers:
            self.logger.error("Still no scrapers available after initialization attempt")
            return 0
        
        all_grievances = []
        
        try:
            # Run all scrapers concurrently
            tasks = [scraper.scrape() for scraper in self.scrapers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Scraper {self.scrapers[i].name} failed: {str(result)}")
                    continue
                    
                all_grievances.extend(result)
            
            # Store grievances
            stored_count = await self._store_grievances(all_grievances)
            
            self.logger.info(f"Scraper run completed. Found {len(all_grievances)} grievances, stored {stored_count}")
            return stored_count
        except Exception as e:
            self.logger.error(f"Error running scrapers: {e}")
            return 0
    
    async def run_scraper(self, scraper_name: str) -> int:
        """
        Run a specific scraper by name.
        Returns the number of new grievances found.
        """
        if not self.scrapers:
            self.logger.warning("No scrapers initialized. Attempting to initialize now.")
            try:
                self._initialize_scrapers()
            except Exception as e:
                self.logger.error(f"Failed to initialize scrapers: {e}")
                return 0
        
        for scraper in self.scrapers:
            if scraper.name.lower() == scraper_name.lower():
                self.logger.info(f"Running scraper: {scraper.name}")
                
                try:
                    grievances = await scraper.scrape()
                    stored_count = await self._store_grievances(grievances)
                    
                    self.logger.info(f"Scraper {scraper.name} completed. Found {len(grievances)} grievances, stored {stored_count}")
                    return stored_count
                except Exception as e:
                    self.logger.error(f"Scraper {scraper.name} failed: {str(e)}")
                    return 0
        
        self.logger.error(f"Scraper not found: {scraper_name}")
        return 0
    
    async def _store_grievances(self, grievances: List[Dict[str, Any]]) -> int:
        """
        Store scraped grievances in the database.
        Returns the number of grievances stored.
        """
        if not grievances:
            self.logger.info("No grievances to store")
            return 0
            
        stored_count = 0
        
        for grievance_dict in grievances:
            try:
                # Generate ticket ID
                ticket_id = f"SC{uuid.uuid4().hex[:8].upper()}"
                
                # Convert dictionary to GrievanceCreate object
                from app.models.grievance import GrievanceCreate
                
                grievance_create = GrievanceCreate(
                    name=grievance_dict.get("name", "Anonymous"),
                    email=grievance_dict.get("email", "no-email@example.com"),
                    phone=grievance_dict.get("phone", "0000000000"),
                    country=grievance_dict.get("country", "India"),
                    state=grievance_dict.get("state", "Unknown"),
                    city=grievance_dict.get("city", "Unknown"),
                    category=grievance_dict.get("category", "Others"),
                    heading=grievance_dict.get("heading", "Unknown Issue"),
                    description=grievance_dict.get("description", "No description provided"),
                    attachment_url=grievance_dict.get("attachment_url")
                )
                
                # Store in database
                self.db.create_grievance(
                    grievance=grievance_create,
                    ticket_id=ticket_id,
                    source=grievance_dict.get("source", "unknown"),
                    source_url=grievance_dict.get("source_url")
                )
                
                self.logger.info(f"Stored grievance with ticket ID: {ticket_id}")
                stored_count += 1
            except Exception as e:
                self.logger.error(f"Error storing grievance: {str(e)}")
        
        return stored_count
