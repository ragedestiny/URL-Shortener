import os
import typer
import requests
from pydantic import ValidationError
from app.models import schemas
from dotenv import load_dotenv
load_dotenv()

# Load environment variables
SERVER_URL = os.getenv("SERVER_URL_PROD") if os.getenv("PRODUCTION") else os.getenv("SERVER_URL_DEV", "localhost")

# Create a Typer instance for user-related commands
admin_app = typer.Typer()


@admin_app.command()
def list_all_urls(token: str):
    """
    Retrieve all short URL to long URL pairs.
    
    Args:
        token (str): Access token for authentication.
    """
    url = f"{SERVER_URL}/list_urls"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        typer.echo("Here are all the URLs:")
        url_pairs = response.json()
        for pair in url_pairs:
            typer.echo(pair)
    else:
        typer.echo(f"Error: {response.text}")
        
        
@admin_app.command()
def update_url_limit(user_email: str, new_limit: int, token: str):
    """
    Update the URL limit for a user.

    Args:
        user_email (str): Email of the user to update the URL limit.
        new_limit (int): New URL limit for the user.
        token (str): Access token for authentication.
    """
    # Validate input data using the Pydantic schemas
    try:
        schemas.Email(email=user_email)
    except ValidationError as e:
        typer.echo(f"Error: {str(e)}")
        return
    
    url = f"{SERVER_URL}/update_url_limit"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"new_limit": new_limit}
    data = { "email": user_email }
    response = requests.patch(url, headers=headers, json=data, params=params)

    if response.status_code == 200:
        typer.echo("URL limit updated successfully.")
    else:
        typer.echo(f"Error: {response.text}")
        

if __name__ == "__main__":
    admin_app()