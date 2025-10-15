from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.models.grievance import GrievanceInDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseScraper(ABC):
    """
    Base abstract class for all scrapers.
    """
    
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.logger = logging.getLogger(f"scraper.{name}")
    
    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape data from the source.
        Returns a list of dictionaries containing grievance data.
        """
        pass
    
    def map_to_grievance(self, data: Dict[str, Any], ticket_id: str) -> GrievanceInDB:
        """
        Map scraped data to GrievanceInDB model.
        """
        return GrievanceInDB(
            ticket_id=ticket_id,
            name=data.get("name", "Anonymous"),
            email=data.get("email", "no-email@example.com"),
            phone=data.get("phone", "0000000000"),
            country=data.get("country", "India"),
            state=data.get("state", "Unknown"),
            city=data.get("city", "Unknown"),
            category=data.get("category", "Others"),
            heading=data.get("heading", "Unknown Issue"),
            description=data.get("description", "No description provided"),
            timestamp=data.get("timestamp", datetime.now()),
            resolved=data.get("resolved", False),
            attachment_url=data.get("attachment_url"),
            source=data.get("source", self.name),
            source_url=data.get("source_url", self.url)
        )
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """
        Log an error with the scraper.
        """
        if exception:
            self.logger.error(f"{message}: {str(exception)}")
        else:
            self.logger.error(message)
    
    def log_info(self, message: str):
        """
        Log an informational message.
        """
        self.logger.info(message)
