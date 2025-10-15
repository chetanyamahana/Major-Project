import asyncio
from typing import List, Dict, Any
from datetime import datetime
import re
import tweepy
import uuid

from app.scrapers.base_scraper import BaseScraper
from app.config.settings import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_SEARCH_QUERIES
)

class TwitterScraper(BaseScraper):
    """
    Scraper for Twitter posts related to civic issues.
    """
    
    def __init__(self, name: str = "Twitter", url: str = "https://twitter.com"):
        super().__init__(name, url)
        self.api = self._setup_api()
        self.search_queries = TWITTER_SEARCH_QUERIES
        
    def _setup_api(self):
        """
        Set up Twitter API client.
        """
        try:
            auth = tweepy.OAuth1UserHandler(
                TWITTER_API_KEY,
                TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_TOKEN_SECRET
            )
            return tweepy.API(auth)
        except Exception as e:
            self.log_error("Failed to set up Twitter API", e)
            return None
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape grievance-related tweets.
        If Twitter API is not available, generate mock data.
        """
        self.log_info("Starting Twitter scrape")
        
        # If Twitter API is not initialized, use mock data
        if not self.api:
            self.log_info("Twitter API not initialized, using mock data")
            return self._generate_mock_tweets()
            
        grievances = []
        
        # Try using the real API
        try:
            # Run in a thread pool since tweepy is synchronous
            loop = asyncio.get_event_loop()
            for query in self.search_queries:
                try:
                    tweets = await loop.run_in_executor(
                        None, 
                        lambda q=query: self.api.search_tweets(q=q, count=100, tweet_mode="extended", lang="en")
                    )
                    
                    for tweet in tweets:
                        grievance = self._process_tweet(tweet)
                        if grievance:
                            grievances.append(grievance)
                            
                    self.log_info(f"Processed {len(tweets)} tweets for query '{query}'")
                    
                except Exception as e:
                    self.log_error(f"Error searching Twitter for query '{query}'", e)
            
            self.log_info(f"Scraped {len(grievances)} grievances from Twitter")
            return grievances
        except Exception as e:
            self.log_error(f"Error using Twitter API, falling back to mock data: {e}")
            return self._generate_mock_tweets()
            
    def _generate_mock_tweets(self) -> List[Dict[str, Any]]:
        """
        Generate mock tweet data for testing.
        """
        self.log_info("Generating mock Twitter data")
        
        # Sample tweet data
        mock_tweets = [
            {
                "name": "Delhi Resident",
                "email": "delhi_resident@twitter.example.com",
                "phone": "9876543210",
                "country": "India",
                "state": "Delhi",
                "city": "New Delhi",
                "category": "Roads & Infrastructure",
                "heading": "Huge pothole on Ring Road near AIIMS causing traffic...",
                "description": "Huge pothole on Ring Road near AIIMS causing traffic jams and accidents. It's been there for weeks and no action taken. @DelhiTrafficPol @mcd_delhi please fix it urgently!",
                "timestamp": datetime.now(),
                "source": "Twitter",
                "source_url": "https://twitter.com/example/status/123456789",
                "resolved": False
            },
            {
                "name": "Mumbai Citizen",
                "email": "mumbai_citizen@twitter.example.com",
                "phone": "8765432109",
                "country": "India",
                "state": "Maharashtra",
                "city": "Mumbai",
                "category": "Waste Management",
                "heading": "Garbage not collected in Andheri West for 3 days...",
                "description": "Garbage not collected in Andheri West for 3 days now. The entire street smells terrible and it's a health hazard. @mybmc please take immediate action! #SwachhBharat",
                "timestamp": datetime.now(),
                "source": "Twitter",
                "source_url": "https://twitter.com/example/status/223456789",
                "resolved": False
            },
            {
                "name": "Bangalore Tech",
                "email": "blr_tech@twitter.example.com",
                "phone": "7654321098",
                "country": "India",
                "state": "Karnataka",
                "city": "Bangalore",
                "category": "Water Supply",
                "heading": "No water supply in Koramangala for the past 24 ho...",
                "description": "No water supply in Koramangala for the past 24 hours. No information provided about when it will be restored. Many IT companies and residences affected. @BWSSB please update!",
                "timestamp": datetime.now(),
                "source": "Twitter",
                "source_url": "https://twitter.com/example/status/323456789",
                "resolved": False
            },
            {
                "name": "Chennai Updates",
                "email": "chennai_updates@twitter.example.com",
                "phone": "6543210987",
                "country": "India",
                "state": "Tamil Nadu",
                "city": "Chennai",
                "category": "Street Lights",
                "heading": "Street lights not working on OMR road for the pas...",
                "description": "Street lights not working on OMR road for the past week. It's very dangerous for commuters at night. @chennaicorp please fix this issue before any accidents happen.",
                "timestamp": datetime.now(),
                "source": "Twitter",
                "source_url": "https://twitter.com/example/status/423456789",
                "resolved": False
            },
            {
                "name": "Kolkata Voice",
                "email": "kolkata_voice@twitter.example.com",
                "phone": "5432109876",
                "country": "India",
                "state": "West Bengal",
                "city": "Kolkata",
                "category": "Sewage & Drainage",
                "heading": "Severe waterlogging in Salt Lake Sector V after j...",
                "description": "Severe waterlogging in Salt Lake Sector V after just 30 minutes of rain. Drainage system completely failed. IT employees unable to reach offices. @KolkataPolice @KMCKolkata please address this recurring issue!",
                "timestamp": datetime.now(),
                "source": "Twitter",
                "source_url": "https://twitter.com/example/status/523456789",
                "resolved": False
            }
        ]
        
        self.log_info(f"Generated {len(mock_tweets)} mock tweets")
        return mock_tweets
    
    def _process_tweet(self, tweet) -> Dict[str, Any]:
        """
        Process a tweet into a grievance.
        """
        try:
            # Get full text (handle retweets)
            if hasattr(tweet, "retweeted_status"):
                text = tweet.retweeted_status.full_text
            else:
                text = tweet.full_text
                
            # Skip if too short
            if len(text) < 20:
                return None
                
            # Extract location information
            location = "Unknown"
            state = "Unknown"
            city = "Unknown"
            
            if tweet.user.location:
                location = tweet.user.location
                # Try to extract city and state
                location_parts = [part.strip() for part in re.split(r'[,|]', location)]
                if len(location_parts) >= 2:
                    city = location_parts[0]
                    state = location_parts[1]
                elif len(location_parts) == 1:
                    city = location_parts[0]
            
            # Determine category based on tweet content
            category = self._categorize_tweet(text)
            
            # Create grievance
            grievance = {
                "name": tweet.user.name,
                "email": f"{tweet.user.screen_name}@twitter.example.com",  # Placeholder email
                "phone": "0000000000",  # Placeholder phone
                "country": "India",  # Assuming India as per requirements
                "state": state,
                "city": city,
                "category": category,
                "heading": text[:50] + ("..." if len(text) > 50 else ""),
                "description": text,
                "timestamp": tweet.created_at,
                "source": "Twitter",
                "source_url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                "resolved": False
            }
            
            return grievance
            
        except Exception as e:
            self.log_error("Error processing tweet", e)
            return None
    
    def _categorize_tweet(self, text: str) -> str:
        """
        Categorize a tweet based on its content.
        """
        text_lower = text.lower()
        
        categories = {
            "Roads & Infrastructure": ["road", "pothole", "street", "highway", "footpath", "bridge", "infrastructure"],
            "Water Supply": ["water supply", "water shortage", "drinking water", "tap water", "water crisis"],
            "Waste Management": ["garbage", "waste", "trash", "dump", "litter", "cleaning", "swachh"],
            "Electricity": ["electricity", "power cut", "power outage", "electric", "transformer"],
            "Public Transport": ["bus", "train", "metro", "public transport", "transportation"],
            "Street Lights": ["street light", "streetlight", "light pole", "dark street"],
            "Sewage & Drainage": ["sewage", "drainage", "drain", "gutter", "waterlogging", "flood"],
            "Parks & Recreation": ["park", "playground", "garden", "recreation"],
            "Public Safety": ["safety", "crime", "police", "security", "unsafe"],
            "Healthcare": ["hospital", "clinic", "health", "medical", "doctor"],
            "Education": ["school", "college", "education", "university", "student"]
        }
        
        # Check each category
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "Others"
