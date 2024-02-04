from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from typing import Optional

from models import schemas
from service.idgenerator import randomID
from models.database import Urls

app = FastAPI()

@app.get("/")
def test():
    return { 'Hello': 'World' }

# grab all url pairs
@app.get("/list_urls")
def getAll() -> dict:
    """
    Get request to retrieve all short url to long url pairs

    Returns:
        dict: All short url to long url pairs
    """
    urlPairs = { x.short_url:x.long_url for x in Urls.scan()}
    
    return urlPairs


# request body should include long url to shorten and an optional short url
@app.post("/shorten_url")
def toShorten(long_url: schemas.longURL, shorturl: Optional[schemas.shortURL] = None) -> dict:
    """Given a long url and optional short url, auto generate short url if not given, create this short url to long url pair and send it to database.

    Args:
        long_url (schemas.longURL): long url to shorted
        short_url (Optional[schemas.shortURL], optional): user specified short url. Defaults to None.

    Raises:
        HTTPException: short url exists in database

    Returns:
        dict: { 'short_url' : short url }
    """
    
    # when no short url given, generate one
    if shorturl == None:
        shorturl = randomID()
        result = { each for each in Urls.query(shorturl)}
        while len(result) != 0: # check and keep generating if there is a collision
            shorturl = randomID()
            result = { each for each in Urls.query(shorturl)}
        shorturl = schemas.shortURL(short_Url=shorturl)
    
    # if short url is in database, send error
    for _ in Urls.query(shorturl.short_Url):
        raise HTTPException(status_code=400, detail=f"Short url {shorturl.short_Url} already exist, try another one.")
    
    # create url pair and save to database
    Urlpair = Urls(short_url = shorturl.short_Url, long_url = str(long_url.url))
    Urlpair.save()
    
    return { 'short_url': shorturl.short_Url }
    

# url parems for redirect to long URL
@app.get("/redirect/{shorturl}")
def getLongUrl(shorturl: str):
    """Using the shorturl parems, find short url in database then redirect to long url if found.

    Args:
        short_URL (str): short url entered as parems

    Raises:
        HTTPException: short url is not in our database, return error

    Returns:
        _type_: redirects to long url if url short is valid
    """
    for found in Urls.query(shorturl): # check to see if short URL exist in our data
        return RedirectResponse(found.long_url)
    
    raise HTTPException(status_code=400, detail=f"Short URL of {shorturl} doesn't exist.")
    
