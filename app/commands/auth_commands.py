import os
import typer
import requests
from pydantic import ValidationError
from app.models import schemas
from dotenv import load_dotenv
load_dotenv()

# Load environment variables
SERVER_URL = os.getenv("SERVER_URL_PROD") if os.getenv("PRODUCTION") else os.getenv("SERVER_URL_DEV", "localhost")

# Create a Typer instance for authentication commands
auth_app = typer.Typer()

@auth_app.command()
def login(username: str, password: str):
    """
    Log in and retrieve access token.

    Args:
        username (str): Username (email) of the user.
        password (str): Password of the user.
    """
    # Validate input data using the Pydantic schemas
    
    try:
        schemas.Email(email=username)
        schemas.Password(password=password)
    except ValidationError as e:
        typer.echo(f"Error: {str(e)}")
        return 
    
    url = f"{SERVER_URL}/login"
    data = {"username": username, "password": password}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        typer.echo(f"Access token: {token}")
    else:
        typer.echo(f"Error: {response.text}")
    

if __name__ == "__main__":
    auth_app()