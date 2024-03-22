import os
import typer
import requests
from pydantic import ValidationError
from app.models import schemas
from dotenv import load_dotenv
load_dotenv()

# Load environment variables
SERVER_URL = os.getenv("SERVER_URL_PROD") if os.getenv("PRODUCTION") else os.getenv("SERVER_URL_DEV", "localhost")

url_app = typer.Typer()

@url_app.command()
def lookup_url(short_url: str):
    """Lookup the long URL associated with the provided short URL."""
    
    try:
        schemas.shortURL(short_Url=short_url)
    except ValidationError as e:
        typer.echo(f"Error: {str(e)}")
        return     
    
    url = f"{SERVER_URL}/lookupURL"
    # Send GET request to the endpoint
    response = requests.get(f"{url}?shorturl={short_url}")
    
    # Check if the request was successful
    if response.status_code == 200:
        # Extract the long URL from the response JSON
        long_url = response.json()["long_url"]
        typer.echo(f"Long URL for {short_url}: {long_url}")
    else:
        # Print error message if request failed
        typer.echo(f"Error: {response.text}")

if __name__ == "__main__":
    url_app()