import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.config.settings import (
    GOOGLE_SHEETS_CREDENTIALS_FILE,
    GOOGLE_SHEETS_TOKEN_FILE,
    GOOGLE_SHEETS_SPREADSHEET_ID,
)
from app.models.grievance import GrievanceInDB, GrievanceCreate

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsDB:
    """
    Google Sheets database integration for storing grievance data.
    """
    
    def __init__(self):
        self.spreadsheet_id = GOOGLE_SHEETS_SPREADSHEET_ID
        try:
            self.service = self._get_service()
            self._setup_sheets()
        except Exception as e:
            print(f"Warning: Google Sheets integration not available: {e}")
            print("Using mock database instead. Data will not be persisted.")
            self.service = None
        
    def _get_service(self):
        """
        Get Google Sheets API service.
        """
        creds = None
        
        # Check if token file exists
        if os.path.exists(GOOGLE_SHEETS_TOKEN_FILE):
            with open(GOOGLE_SHEETS_TOKEN_FILE, 'r') as token:
                creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
                
        # If credentials don't exist or are invalid, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_SHEETS_CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save the credentials for the next run
            with open(GOOGLE_SHEETS_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
                
        # Build the service
        service = build('sheets', 'v4', credentials=creds)
        return service
    
    def _setup_sheets(self):
        """
        Set up the required sheets if they don't exist.
        """
        # Get existing sheets
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheet_names = [sheet['properties']['title'] for sheet in sheets]
        
        # Check if Grievances sheet exists, if not create it
        if 'Grievances' not in sheet_names:
            self._create_grievances_sheet()
    
    def _create_grievances_sheet(self):
        """
        Create the Grievances sheet with headers.
        """
        # Create a new sheet
        batch_update_request = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': 'Grievances'
                    }
                }
            }]
        }
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=batch_update_request
        ).execute()
        
        # Add headers
        headers = [
            'Ticket ID', 'Name', 'Email', 'Phone', 'Country', 'State', 'City',
            'Category', 'Heading', 'Description', 'Timestamp', 'Resolved',
            'Attachment URL', 'Source', 'Source URL'
        ]
        
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range='Grievances!A1:O1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
    
    # In-memory storage for mock database
    _mock_grievances = []
    
    def create_grievance(self, grievance: GrievanceCreate, ticket_id: str, source: str = "user_submission", source_url: Optional[str] = None) -> GrievanceInDB:
        """
        Create a new grievance record in Google Sheets or mock database.
        """
        # Convert to GrievanceInDB
        db_grievance = GrievanceInDB(
            ticket_id=ticket_id,
            name=grievance.name,
            email=grievance.email,
            phone=grievance.phone,
            country=grievance.country,
            state=grievance.state,
            city=grievance.city,
            category=grievance.category,
            heading=grievance.heading,
            description=grievance.description,
            timestamp=datetime.now(),
            resolved=False,
            attachment_url=grievance.attachment_url,
            source=source,
            source_url=source_url
        )
        
        if self.service:
            # Prepare data for Google Sheets
            values = [
                [
                    db_grievance.ticket_id,
                    db_grievance.name,
                    db_grievance.email,
                    db_grievance.phone,
                    db_grievance.country,
                    db_grievance.state,
                    db_grievance.city,
                    db_grievance.category,
                    db_grievance.heading,
                    db_grievance.description,
                    db_grievance.timestamp.isoformat(),
                    str(db_grievance.resolved),
                    db_grievance.attachment_url or '',
                    db_grievance.source,
                    db_grievance.source_url or ''
                ]
            ]
            
            # Append to sheet
            try:
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range='Grievances!A:O',
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': values}
                ).execute()
            except Exception as e:
                print(f"Error storing grievance in Google Sheets: {e}")
                # Fall back to mock storage
                self._mock_grievances.append(db_grievance)
        else:
            # Store in mock database
            self._mock_grievances.append(db_grievance)
            print(f"Stored grievance {ticket_id} in mock database")
        
        return db_grievance
    
    def get_grievances(self, skip: int = 0, limit: int = 100) -> List[GrievanceInDB]:
        """
        Get a list of grievances from Google Sheets or mock database.
        """
        if not self.service:
            # Use mock database
            return self._mock_grievances[skip:skip+limit]
            
        try:
            # Get all data from sheet
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Grievances!A:O'
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) <= 1:  # Only headers or empty
                return []
            
            # Extract headers and data
            headers = values[0]
            data = values[1:]  # Skip headers
            
            # Apply pagination
            paginated_data = data[skip:skip+limit]
            
            # Convert to GrievanceInDB objects
            grievances = []
            for row in paginated_data:
                # Pad row if necessary
                padded_row = row + [''] * (len(headers) - len(row))
                
                # Create a dictionary mapping headers to values
                grievance_dict = dict(zip(headers, padded_row))
                
                # Convert to GrievanceInDB
                grievance = GrievanceInDB(
                    ticket_id=grievance_dict['Ticket ID'],
                    name=grievance_dict['Name'],
                    email=grievance_dict['Email'],
                    phone=grievance_dict['Phone'],
                    country=grievance_dict['Country'],
                    state=grievance_dict['State'],
                    city=grievance_dict['City'],
                    category=grievance_dict['Category'],
                    heading=grievance_dict['Heading'],
                    description=grievance_dict['Description'],
                    timestamp=datetime.fromisoformat(grievance_dict['Timestamp']) if grievance_dict['Timestamp'] else datetime.now(),
                    resolved=grievance_dict['Resolved'].lower() == 'true',
                    attachment_url=grievance_dict['Attachment URL'] if grievance_dict['Attachment URL'] else None,
                    source=grievance_dict['Source'],
                    source_url=grievance_dict['Source URL'] if grievance_dict['Source URL'] else None
                )
                
                grievances.append(grievance)
            
            return grievances
        except Exception as e:
            print(f"Error fetching grievances from Google Sheets: {e}")
            # Fall back to mock database
            return self._mock_grievances[skip:skip+limit]
    
    def get_grievance_by_id(self, ticket_id: str) -> Optional[GrievanceInDB]:
        """
        Get a specific grievance by its ticket ID.
        """
        if not self.service:
            # Use mock database
            for grievance in self._mock_grievances:
                if grievance.ticket_id == ticket_id:
                    return grievance
            return None
            
        try:
            # Get all data from sheet
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Grievances!A:O'
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) <= 1:  # Only headers or empty
                return None
            
            # Extract headers and data
            headers = values[0]
            data = values[1:]  # Skip headers
            
            # Find the row with matching ticket_id
            for row in data:
                if row and row[0] == ticket_id:
                    # Pad row if necessary
                    padded_row = row + [''] * (len(headers) - len(row))
                    
                    # Create a dictionary mapping headers to values
                    grievance_dict = dict(zip(headers, padded_row))
                    
                    # Convert to GrievanceInDB
                    return GrievanceInDB(
                        ticket_id=grievance_dict['Ticket ID'],
                        name=grievance_dict['Name'],
                        email=grievance_dict['Email'],
                        phone=grievance_dict['Phone'],
                        country=grievance_dict['Country'],
                        state=grievance_dict['State'],
                        city=grievance_dict['City'],
                        category=grievance_dict['Category'],
                        heading=grievance_dict['Heading'],
                        description=grievance_dict['Description'],
                        timestamp=datetime.fromisoformat(grievance_dict['Timestamp']) if grievance_dict['Timestamp'] else datetime.now(),
                        resolved=grievance_dict['Resolved'].lower() == 'true',
                        attachment_url=grievance_dict['Attachment URL'] if grievance_dict['Attachment URL'] else None,
                        source=grievance_dict['Source'],
                        source_url=grievance_dict['Source URL'] if grievance_dict['Source URL'] else None
                    )
            
            return None
        except Exception as e:
            print(f"Error fetching grievance by ID from Google Sheets: {e}")
            # Fall back to mock database
            for grievance in self._mock_grievances:
                if grievance.ticket_id == ticket_id:
                    return grievance
            return None
    
    def update_grievance_status(self, ticket_id: str, resolved: bool) -> Optional[GrievanceInDB]:
        """
        Update the resolved status of a grievance.
        """
        if not self.service:
            # Use mock database
            for grievance in self._mock_grievances:
                if grievance.ticket_id == ticket_id:
                    grievance.resolved = resolved
                    return grievance
            return None
            
        try:
            # Get all data from sheet
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Grievances!A:O'
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) <= 1:  # Only headers or empty
                return None
            
            # Find the row with matching ticket_id
            for i, row in enumerate(values[1:], start=2):  # Start from 2 to account for 1-indexed sheets and headers
                if row and row[0] == ticket_id:
                    # Update the resolved status (12th column, index 11)
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=f'Grievances!L{i}',
                        valueInputOption='RAW',
                        body={'values': [[str(resolved)]]}
                    ).execute()
                    
                    # Return the updated grievance
                    return self.get_grievance_by_id(ticket_id)
            
            return None
        except Exception as e:
            print(f"Error updating grievance status in Google Sheets: {e}")
            # Fall back to mock database
            for grievance in self._mock_grievances:
                if grievance.ticket_id == ticket_id:
                    grievance.resolved = resolved
                    return grievance
            return None
    
    def get_grievance_stats(self) -> Dict[str, Any]:
        """
        Get statistics about grievances.
        """
        if not self.service or not self._mock_grievances:
            # Use mock database or return empty stats if no data
            if not self._mock_grievances:
                return {
                    'total_grievances': 0,
                    'resolved_grievances': 0,
                    'pending_grievances': 0,
                    'by_category': {},
                    'by_state': {},
                    'by_source': {}
                }
                
            # Calculate stats from mock database
            total = len(self._mock_grievances)
            resolved = sum(1 for g in self._mock_grievances if g.resolved)
            
            by_category = {}
            by_state = {}
            by_source = {}
            
            for g in self._mock_grievances:
                by_category[g.category] = by_category.get(g.category, 0) + 1
                by_state[g.state] = by_state.get(g.state, 0) + 1
                by_source[g.source] = by_source.get(g.source, 0) + 1
                
            return {
                'total_grievances': total,
                'resolved_grievances': resolved,
                'pending_grievances': total - resolved,
                'by_category': by_category,
                'by_state': by_state,
                'by_source': by_source
            }
            
        try:
            # Get all data from sheet
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Grievances!A:O'
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) <= 1:  # Only headers or empty
                return {
                    'total_grievances': 0,
                    'resolved_grievances': 0,
                    'pending_grievances': 0,
                    'by_category': {},
                    'by_state': {},
                    'by_source': {}
                }
            
            # Extract data (skip headers)
            data = values[1:]
            
            # Initialize counters
            total = len(data)
            resolved = 0
            by_category = {}
            by_state = {}
            by_source = {}
            
            # Process each row
            for row in data:
                if len(row) >= 12:  # Ensure we have enough columns
                    # Count resolved
                    if row[11].lower() == 'true':
                        resolved += 1
                    
                    # Count by category
                    if len(row) >= 8 and row[7]:
                        category = row[7]
                        by_category[category] = by_category.get(category, 0) + 1
                    
                    # Count by state
                    if len(row) >= 6 and row[5]:
                        state = row[5]
                        by_state[state] = by_state.get(state, 0) + 1
                    
                    # Count by source
                    if len(row) >= 14 and row[13]:
                        source = row[13]
                        by_source[source] = by_source.get(source, 0) + 1
            
            # Return statistics
            return {
                'total_grievances': total,
                'resolved_grievances': resolved,
                'pending_grievances': total - resolved,
                'by_category': by_category,
                'by_state': by_state,
                'by_source': by_source
            }
        except Exception as e:
            print(f"Error getting statistics from Google Sheets: {e}")
            # Fall back to mock database
            if not self._mock_grievances:
                return {
                    'total_grievances': 0,
                    'resolved_grievances': 0,
                    'pending_grievances': 0,
                    'by_category': {},
                    'by_state': {},
                    'by_source': {}
                }
                
            # Calculate stats from mock database
            total = len(self._mock_grievances)
            resolved = sum(1 for g in self._mock_grievances if g.resolved)
            
            by_category = {}
            by_state = {}
            by_source = {}
            
            for g in self._mock_grievances:
                by_category[g.category] = by_category.get(g.category, 0) + 1
                by_state[g.state] = by_state.get(g.state, 0) + 1
                by_source[g.source] = by_source.get(g.source, 0) + 1
                
            return {
                'total_grievances': total,
                'resolved_grievances': resolved,
                'pending_grievances': total - resolved,
                'by_category': by_category,
                'by_state': by_state,
                'by_source': by_source
            }
