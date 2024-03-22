from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from typing import Optional
from pydantic import ValidationError
from pynamodb.exceptions import DoesNotExist

from app.models import schemas
from app.service.idgenerator import randomID
from app.models.database import Urls, Users
from app.auth.auth import get_current_user


router = APIRouter()


@router.get("/")
def test():
    return { 'Hello': 'World' }


# request body should include long url to shorten and an optional short url
@router.post("/shorten_url")
def to_shorten(
    long_url: schemas.longURL,
    current_user: Users = Depends(get_current_user),
    short_url: Optional[schemas.shortURL] = None
) -> dict:
    """
    Given a long URL and an optional short URL, auto-generate a short URL if not given.
    Create a URL pair and save it to the database, associating it with the current user.

    Args:
        long_url (schemas.LongURL): Long URL to be shortened.
        current_user (Users): Current logged-in user obtained from JWT token.
        short_url (Optional[schemas.ShortURL], optional): User-specified short URL. Defaults to None.

    Raises:
        HTTPException: If the short URL already exists in the database.

    Returns:
        dict: Dictionary containing the short URL.
    """

    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required to access this endpoint.")
    

    # Check if the user has reached the URL limit
    if len(current_user.urls) >= current_user.url_limit:
        raise HTTPException(status_code=400, detail=f"User has reached the maximum URL limit of {current_user.url_limit} short urls.")
    
    
    # When no short URL is given, generate one
    if short_url is None:
        short_url = randomID()
        while any(Urls.query(short_url)):
            # Generate new random ID if it exists in the database
            short_url = randomID()
        short_url = schemas.shortURL(short_Url=short_url)
    
    # If short URL is in the database, raise an error
    if any(Urls.query(short_url.short_Url)):
        raise HTTPException(status_code=400, detail=f"Short URL {short_url.short_Url} already exists, please try another one.")
    
    # Create URL pair and save it to the database, associating it with the current user
    url_pair = Urls(short_url=short_url.short_Url, long_url=str(long_url.url), creator_email=current_user.email)
    url_pair.save()

    # Append the new URL to the list of URLs for the current user
    current_user.urls.append([short_url.short_Url, str(long_url.url)])
    current_user.save()
    
    return { "short_url": short_url.short_Url, "long_url": str(long_url.url) }
    

@router.delete("/delete_url")
def delete_url(
    short_url: schemas.shortURL,
    current_user: Users = Depends(get_current_user)
) -> dict:
    """
    Delete a URL pair associated with the provided short URL.

    Args:
        short_url (str): Short URL to be deleted.
        current_user (Users): Current logged-in user obtained from JWT token.

    Raises:
        HTTPException: If the provided short URL does not exist or does not belong to the current user.

    Returns:
        dict: Dictionary containing the result of the deletion operation.
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required to access this endpoint.")

    # Check if the short URL exists and belongs to the current user
    try:
        url_pair = Urls.get(short_url.short_Url)
    except DoesNotExist:
        url_pair = None
    if not url_pair or url_pair.creator_email != current_user.email:
        raise HTTPException(status_code=404, detail=f"Short URL '{short_url.short_Url}' not found or does not belong to the current user.")
    
    # Delete the URL pair from the database
    url_pair.delete()

    # Filter out the dictionary with key
    current_user.urls = [[shortUrl, LongUrl] for shortUrl, LongUrl in current_user.urls if shortUrl != short_url.short_Url]
    current_user.save()

    return { "message": f"Short URL '{short_url.short_Url}' deleted successfully." }


# url parems for redirect to long URL
@router.get("/redirect/{shorturl}")
def getLongUrl(shorturl: str):
    """Using the shorturl parems, find short url in database then redirect to long url if found.

    Args:
        short_URL (str): short url entered as parems

    Raises:
        HTTPException: short url is not in our database, return error

    Returns:
        _type_: redirects to long url if url short is valid
    """
    
    # retrieve shorturl pair from database
    result = list(Urls.query(shorturl))
    
    # check to see if short URL exist in our data
    if not any(result):
        raise HTTPException(status_code=400, detail=f"Short URL of {shorturl} doesn't exist.")
    
    # redirect to page if short url does exist    
    return RedirectResponse(result[0].long_url)



@router.get("/lookupURL")
def lookupLongUrl(shorturl: str):
    """Find short url in database then return long url if found.

    Args:
        short_URL (str): short url

    Raises:
        HTTPException: short url is not in our database, return error

    Returns:
        _type_: long url
    """
    
    # Retrieve short URL pair from the database
    result = list(Urls.query(shorturl))
    
    # Check if the short URL exists in the database
    if not any(result):
        raise HTTPException(status_code=400, detail=f"Short URL '{shorturl}' doesn't exist.")
    
    # Return the long URL
    return {"long_url": result[0].long_url}
