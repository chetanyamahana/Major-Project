from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class GrievanceBase(BaseModel):
    """Base model for grievance data."""
    category: str
    heading: str
    description: str
    country: str = Field(default="India")
    state: str
    city: str
    
class GrievanceCreate(GrievanceBase):
    """Model for creating a new grievance."""
    name: str
    email: str
    phone: str
    attachment_url: Optional[str] = None
    
class GrievanceInDB(GrievanceBase):
    """Model for grievance stored in database."""
    ticket_id: str
    name: str
    email: str
    phone: str
    timestamp: datetime = Field(default_factory=datetime.now)
    resolved: bool = False
    attachment_url: Optional[str] = None
    source: str = "user_submission"  # user_submission, twitter, municipality_portal, etc.
    source_url: Optional[str] = None
    
class GrievanceResponse(GrievanceInDB):
    """Model for API response."""
    pass

class GrievanceList(BaseModel):
    """Model for list of grievances."""
    items: List[GrievanceResponse]
    total: int
    
class GrievanceStats(BaseModel):
    """Model for grievance statistics."""
    total_grievances: int
    resolved_grievances: int
    pending_grievances: int
    by_category: dict
    by_state: dict
    by_source: dict
