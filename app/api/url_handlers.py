from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from typing import Optional

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
    current_user.urls.append({"short_url": short_url.short_Url, "long_url": str(long_url.url)})
    current_user.save()
    
    return {'short_url': short_url.short_Url}
    

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


