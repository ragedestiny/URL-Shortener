import os
import typer
import requests
from pydantic import ValidationError
from app.models import schemas
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

# Load environment variables
SERVER_URL = os.getenv("SERVER_URL_PROD") if os.getenv("PRODUCTION") else os.getenv("SERVER_URL_DEV", "localhost")

# Create a Typer instance for user-related commands
user_app = typer.Typer()

@user_app.command()
def create_user(email: str, password: str):
    """
    Create a new user account.

    Args:
        email (str): Email address for the new user.
        password (str): Password for the new user.
    """
    # Validate input data using the Pydantic schemas
    try:
        schemas.Email(email=email)
        schemas.Password(password=password)
    except ValidationError as e:
        typer.echo(f"Error: {str(e)}")
        return
    
    userObj = {
        "user_email": {
            "email": email
        },
        "user_password": {
            "password": password
        }
    }
    
    url = f"{SERVER_URL}/create_user"
    response = requests.post(url, json=userObj)
    if response.status_code == 200:
        typer.echo("User account created successfully.")
    else:
        typer.echo(f"Error: {response.text}")
        
        
@user_app.command()
def list_my_urls(token: str):
    """
    List URLs associated with the authenticated user.

    Args:
        token (str): Access token for authentication.
    """
    url = f"{SERVER_URL}/list_my_urls"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        urls = response.json()
        typer.echo("Here is your URL list:")
        for each_url in urls:
            typer.echo(each_url)
    else:
        typer.echo(f"Error: {response.text}")
        

@user_app.command()
def change_password(new_password: str, token: str):
    """
    Change the password for the authenticated user.

    Args:
        new_password (str): New password for the user.
        token (str): Access token for authentication.
    """
    # Validate input data using the Pydantic schemas
    try:
        schemas.Password(password=new_password)
    except ValidationError as e:
        typer.echo(f"Error: {str(e)}")
        return
    
    url = f"{SERVER_URL}/change_password"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"password": new_password}  # Send new_password as a query parameter
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        typer.echo("Password changed successfully.")
    else:
        typer.echo(f"Error: {response.text}")
        
        
        
@user_app.command()
def shorten_url(long_url: str, token: str, short_url: Optional[str] = None):
    """
    Shorten a long URL.

    Args:
        long_url (str): Long URL to be shortened.
        token (str): Access token for authentication.
        short_url (str, optional): User-specified short URL. Defaults to None.
    """
    
    # Validate input data using the Pydantic schemas
    try:
        schemas.longURL(url=long_url)
        if short_url:
            schemas.shortURL(short_Url=short_url)
    except ValidationError as e:
        typer.echo(f"Error: {str(e)}")
        return
    
    url = f"{SERVER_URL}/shorten_url"
    headers = {"Authorization": f"Bearer {token}"}
    
    # request body to send
    if short_url:
        UrlsObj = {
            "long_url": {
                "url": long_url
            },
            "short_url": {
                "short_Url": short_url
            }
        }
    else:
        UrlsObj = {
            "long_url": {
                "url": long_url
            }
        }
        
    response = requests.post(url, headers=headers, json=UrlsObj)

    if response.status_code == 200:
        result = response.json()
        typer.echo(f"Short URL: {result['short_url']}")
    else:
        typer.echo(f"Error: {response.text}")


if __name__ == "__main__":
    user_app()