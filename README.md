# CivicSense - Grievance Redressal System

A comprehensive system for collecting, managing, and analyzing civic grievances from multiple sources.

## Features

- **User Grievance Submission**: Web interface for citizens to report civic issues
- **Data Scraping**: Automatically collects grievances from:
  - Municipality websites
  - Government portals
  - Twitter posts related to civic issues
- **Dashboard**: Admin interface to view and manage grievances
- **Google Sheets Integration**: Simple database solution for the POC

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Database**: Google Sheets API
- **Scraping**: BeautifulSoup, Tweepy

## Project Structure

```
.
├── app/
│   ├── api/            # FastAPI routes and application
│   ├── config/         # Configuration settings
│   ├── db/             # Database integration
│   ├── models/         # Pydantic models
│   ├── scrapers/       # Web scraping modules
│   ├── services/       # Business logic
│   └── utils/          # Helper utilities
├── tests/              # Test cases
├── dashboard.html      # Admin dashboard UI
├── upload_page.html    # Grievance submission form
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix/MacOS
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up Google Sheets API:
   - Create a project in Google Cloud Console
   - Enable Google Sheets API
   - Create credentials (OAuth client ID)
   - Download credentials as `credentials.json` in project root
   - Create a Google Sheet and note its ID

5. Create a `.env` file with the following:
   ```
   GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
   GOOGLE_SHEETS_TOKEN_FILE=token.json
   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
   
   # Twitter API credentials (if using Twitter scraping)
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   TWITTER_ACCESS_TOKEN=your_twitter_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
   ```

6. Run the application:
   ```
   python main.py
   ```

7. Access the application:
   - Grievance submission form: http://localhost:8000/
   - Admin dashboard: http://localhost:8000/dashboard

## API Endpoints

- `POST /api/v1/grievances/`: Submit a new grievance
- `GET /api/v1/grievances/`: List all grievances (with pagination)
- `GET /api/v1/grievances/{ticket_id}`: Get details of a specific grievance
- `PATCH /api/v1/grievances/{ticket_id}/status`: Update grievance status
- `GET /api/v1/stats/`: Get grievance statistics
- `POST /api/v1/scrape/`: Trigger scraping from all sources
- `POST /api/v1/scrape/{source}`: Trigger scraping from a specific source

## Future Enhancements

- File upload functionality for attachments
- User authentication and authorization
- More sophisticated database (MongoDB, PostgreSQL)
- Mobile application
- Natural language processing for grievance categorization
- Integration with more government portals
- Email notifications for status updates
- Geographic visualization of grievances