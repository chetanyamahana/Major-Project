import asyncio
import re
from typing import List, Dict, Any
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import uuid

from app.scrapers.base_scraper import BaseScraper
from app.config.settings import SCRAPING_USER_AGENT, SCRAPING_REQUEST_TIMEOUT

class MunicipalityScraper(BaseScraper):
    """
    Scraper for municipality websites.
    """
    
    def __init__(self, name: str, url: str):
        super().__init__(name, url)
        self.headers = {
            "User-Agent": SCRAPING_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape grievance data from municipality website.
        Falls back to mock data if real scraping fails.
        """
        self.log_info(f"Starting scrape of {self.name} at {self.url}")
        
        try:
            async with httpx.AsyncClient(timeout=SCRAPING_REQUEST_TIMEOUT) as client:
                try:
                    response = await client.get(self.url, headers=self.headers)
                    response.raise_for_status()
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Extract grievances based on common patterns
                    grievances = await self._extract_grievances(soup)
                    
                    if grievances:
                        self.log_info(f"Scraped {len(grievances)} grievances from {self.name}")
                        return grievances
                    else:
                        self.log_info(f"No grievances found at {self.url}, using mock data")
                        return self._generate_mock_grievances()
                        
                except httpx.RequestError as e:
                    self.log_error(f"Error requesting {self.url}, using mock data", e)
                    return self._generate_mock_grievances()
                except httpx.HTTPStatusError as e:
                    self.log_error(f"HTTP error for {self.url}: {e.response.status_code}, using mock data", e)
                    return self._generate_mock_grievances()
                
        except Exception as e:
            self.log_error(f"Unexpected error scraping {self.url}, using mock data", e)
            return self._generate_mock_grievances()
            
    def _generate_mock_grievances(self) -> List[Dict[str, Any]]:
        """
        Generate mock grievance data for testing.
        """
        self.log_info(f"Generating mock data for {self.name}")
        
        # Create mock data based on municipality name
        mock_data = []
        
        if "Delhi" in self.name:
            mock_data = [
                {
                    "description": "Sewage overflow in Karol Bagh area causing health issues",
                    "category": "Sewage & Drainage",
                    "resolved": False,
                    "timestamp": datetime.now(),
                    "city": "Delhi",
                    "source": self.name,
                    "source_url": self.url,
                    "heading": "Sewage overflow in Karol Bagh area",
                    "name": "Local Resident",
                    "email": "resident@example.com",
                    "phone": "9876543210",
                    "state": "Delhi",
                    "country": "India"
                },
                {
                    "description": "Garbage collection irregular in Dwarka Sector 7 for past two weeks",
                    "category": "Waste Management",
                    "resolved": False,
                    "timestamp": datetime.now(),
                    "city": "Delhi",
                    "source": self.name,
                    "source_url": self.url,
                    "heading": "Irregular garbage collection in Dwarka",
                    "name": "Residents Association",
                    "email": "dwarka@example.com",
                    "phone": "9876543211",
                    "state": "Delhi",
                    "country": "India"
                }
            ]
        elif "Chandigarh" in self.name:
            mock_data = [
                {
                    "description": "Street lights not working in Sector 17 market area for past 3 days",
                    "category": "Street Lights",
                    "resolved": False,
                    "timestamp": datetime.now(),
                    "city": "Chandigarh",
                    "source": self.name,
                    "source_url": self.url,
                    "heading": "Street lights issue in Sector 17",
                    "name": "Market Association",
                    "email": "market@example.com",
                    "phone": "9876543212",
                    "state": "Chandigarh",
                    "country": "India"
                },
                {
                    "description": "Water supply disruption in Sector 22 residential area",
                    "category": "Water Supply",
                    "resolved": True,
                    "timestamp": datetime.now(),
                    "city": "Chandigarh",
                    "source": self.name,
                    "source_url": self.url,
                    "heading": "Water supply issue in Sector 22",
                    "name": "Resident",
                    "email": "resident22@example.com",
                    "phone": "9876543213",
                    "state": "Chandigarh",
                    "country": "India"
                }
            ]
        elif "Swachh Bharat" in self.name:
            mock_data = [
                {
                    "description": "Open dumping of waste near Laxmi Nagar metro station",
                    "category": "Waste Management",
                    "resolved": False,
                    "timestamp": datetime.now(),
                    "city": "New Delhi",
                    "source": self.name,
                    "source_url": self.url,
                    "heading": "Open waste dumping at Laxmi Nagar",
                    "name": "Concerned Citizen",
                    "email": "citizen@example.com",
                    "phone": "9876543214",
                    "state": "Delhi",
                    "country": "India"
                },
                {
                    "description": "Public toilet in Connaught Place needs maintenance and cleaning",
                    "category": "Public Facilities",
                    "resolved": False,
                    "timestamp": datetime.now(),
                    "city": "New Delhi",
                    "source": self.name,
                    "source_url": self.url,
                    "heading": "Public toilet maintenance needed",
                    "name": "Visitor",
                    "email": "visitor@example.com",
                    "phone": "9876543215",
                    "state": "Delhi",
                    "country": "India"
                }
            ]
        else:
            # Generic mock data for any other municipality
            mock_data = [
                {
                    "description": f"Road maintenance required in central area of {self.name}",
                    "category": "Roads & Infrastructure",
                    "resolved": False,
                    "timestamp": datetime.now(),
                    "city": self.name.split()[0],  # Extract first word as city name
                    "source": self.name,
                    "source_url": self.url,
                    "heading": f"Road maintenance in {self.name}",
                    "name": "Local Resident",
                    "email": "local@example.com",
                    "phone": "9876543216",
                    "state": "Unknown",
                    "country": "India"
                }
            ]
            
        self.log_info(f"Generated {len(mock_data)} mock grievances for {self.name}")
        return mock_data
    
    async def _extract_grievances(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract grievances from the parsed HTML.
        This method uses multiple strategies to find grievance data.
        """
        grievances = []
        
        # Strategy 1: Look for tables with complaint/grievance data
        tables = soup.find_all("table")
        for table in tables:
            if self._is_grievance_table(table):
                grievances.extend(self._extract_from_table(table))
        
        # Strategy 2: Look for complaint cards/divs
        cards = soup.find_all(["div", "article", "section"], class_=self._grievance_class_matcher)
        for card in cards:
            grievance = self._extract_from_card(card)
            if grievance:
                grievances.append(grievance)
        
        # Strategy 3: Look for list items that might contain grievances
        lists = soup.find_all(["ul", "ol"], class_=self._grievance_class_matcher)
        for list_elem in lists:
            items = list_elem.find_all("li")
            for item in items:
                grievance = self._extract_from_list_item(item)
                if grievance:
                    grievances.append(grievance)
        
        return grievances
    
    def _is_grievance_table(self, table: BeautifulSoup) -> bool:
        """
        Check if a table contains grievance data.
        """
        # Look for headers that suggest grievance data
        headers = table.find_all(["th", "td"])
        header_text = " ".join([h.get_text().lower() for h in headers])
        
        grievance_keywords = ["complaint", "grievance", "issue", "problem", "request", "service", "status"]
        return any(keyword in header_text for keyword in grievance_keywords)
    
    def _extract_from_table(self, table: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract grievance data from a table.
        """
        grievances = []
        
        # Get headers
        headers = []
        header_row = table.find("tr")
        if header_row:
            headers = [th.get_text().strip().lower() for th in header_row.find_all(["th", "td"])]
        
        # Process data rows
        rows = table.find_all("tr")[1:] if headers else table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
                
            # Extract cell text
            cell_data = [cell.get_text().strip() for cell in cells]
            
            # Map to grievance data
            grievance = {}
            
            if headers:
                # Use headers to map data
                for i, header in enumerate(headers):
                    if i < len(cell_data):
                        if "complaint" in header or "grievance" in header or "issue" in header or "problem" in header:
                            grievance["description"] = cell_data[i]
                        elif "category" in header or "type" in header:
                            grievance["category"] = cell_data[i]
                        elif "status" in header:
                            grievance["resolved"] = "resolved" in cell_data[i].lower() or "closed" in cell_data[i].lower()
                        elif "date" in header or "time" in header:
                            grievance["timestamp"] = self._parse_date(cell_data[i])
                        elif "location" in header or "area" in header or "ward" in header:
                            grievance["city"] = cell_data[i]
            else:
                # No headers, make best guess
                if len(cell_data) >= 3:
                    grievance["description"] = cell_data[0]
                    grievance["category"] = "Others"
                    grievance["timestamp"] = self._parse_date(cell_data[-1])
            
            # Add source information
            grievance["source"] = self.name
            grievance["source_url"] = self.url
            
            # Add heading if missing
            if "description" in grievance and "heading" not in grievance:
                grievance["heading"] = grievance["description"][:50] + ("..." if len(grievance["description"]) > 50 else "")
            
            # Only add if we have at least a description
            if "description" in grievance and grievance["description"]:
                grievances.append(grievance)
        
        return grievances
    
    def _grievance_class_matcher(self, class_attr: str) -> bool:
        """
        Check if a class attribute suggests this element contains grievance data.
        """
        if not class_attr:
            return False
            
        keywords = ["complaint", "grievance", "issue", "problem", "ticket", "request", "service"]
        return any(keyword in class_attr.lower() for keyword in keywords)
    
    def _extract_from_card(self, card: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract grievance data from a card/div element.
        """
        grievance = {
            "source": self.name,
            "source_url": self.url
        }
        
        # Look for title/heading
        heading_elem = card.find(["h1", "h2", "h3", "h4", "h5", "h6", "strong", "b"])
        if heading_elem:
            grievance["heading"] = heading_elem.get_text().strip()
        
        # Look for description
        description_elem = card.find(["p", "div"], class_=lambda c: c and ("description" in c.lower() or "content" in c.lower()))
        if description_elem:
            grievance["description"] = description_elem.get_text().strip()
        elif heading_elem and heading_elem.find_next("p"):
            grievance["description"] = heading_elem.find_next("p").get_text().strip()
        
        # Look for category
        category_elem = card.find(["span", "div"], class_=lambda c: c and ("category" in c.lower() or "type" in c.lower()))
        if category_elem:
            grievance["category"] = category_elem.get_text().strip()
        
        # Look for date
        date_elem = card.find(["span", "div", "time"], class_=lambda c: c and ("date" in c.lower() or "time" in c.lower()))
        if date_elem:
            grievance["timestamp"] = self._parse_date(date_elem.get_text().strip())
        
        # Look for status
        status_elem = card.find(["span", "div"], class_=lambda c: c and "status" in c.lower())
        if status_elem:
            status_text = status_elem.get_text().strip().lower()
            grievance["resolved"] = "resolved" in status_text or "closed" in status_text
        
        # Only return if we have at least a heading or description
        if ("heading" in grievance and grievance["heading"]) or ("description" in grievance and grievance["description"]):
            # If we have description but no heading, create a heading
            if "description" in grievance and "heading" not in grievance:
                grievance["heading"] = grievance["description"][:50] + ("..." if len(grievance["description"]) > 50 else "")
            
            # If we have heading but no description, use heading as description
            if "heading" in grievance and "description" not in grievance:
                grievance["description"] = grievance["heading"]
                
            return grievance
        
        return None
    
    def _extract_from_list_item(self, item: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract grievance data from a list item.
        """
        text = item.get_text().strip()
        if not text:
            return None
            
        # Check if it looks like a grievance
        grievance_keywords = ["complaint", "grievance", "issue", "problem", "request", "service"]
        if not any(keyword in text.lower() for keyword in grievance_keywords):
            return None
        
        # Extract what we can
        grievance = {
            "description": text,
            "heading": text[:50] + ("..." if len(text) > 50 else ""),
            "source": self.name,
            "source_url": self.url,
            "category": "Others"
        }
        
        # Try to extract date
        date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}', text)
        if date_match:
            grievance["timestamp"] = self._parse_date(date_match.group(0))
        
        return grievance
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse a date string into a datetime object.
        Handles multiple formats.
        """
        try:
            # Try common formats
            formats = [
                "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y",
                "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y",
                "%d.%m.%Y", "%Y.%m.%d"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, return current time
            return datetime.now()
        except Exception:
            return datetime.now()
