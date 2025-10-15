import uvicorn
import os
from pathlib import Path

# Ensure the upload_page.html is in the project root
def ensure_html_file():
    """
    Ensure the upload_page.html file is in the project root.
    """
    html_path = Path(__file__).parent / "upload_page.html"
    if not html_path.exists():
        raise FileNotFoundError(f"upload_page.html not found at {html_path}")

if __name__ == "__main__":
    try:
        # Check for required files
        ensure_html_file()
        
        print("Starting Grievance Redressal System...")
        print("Access the application at http://localhost:8000")
        print("Access the dashboard at http://localhost:8000/dashboard")
        print("Note: The application is running in test mode with a mock database.")
        print("      No actual connection to Google Sheets or Twitter API will be made.")
        print("      All data will be stored in memory and lost when the application is stopped.")
        
        # Start the server
        uvicorn.run(
            "app.api.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Please make sure you have all the required files and dependencies installed.")
        print("Run 'pip install -r requirements.txt' to install all dependencies.")
