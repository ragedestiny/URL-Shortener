from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from typing import Optional

from models import schemas
from models.testurls import urlMap
from service.idgenerator import randomID

app = FastAPI()

@app.get("/")
def test():
    return { 'Hello': 'World' }

# grab all url pairs
@app.get("/list_urls")
def getAll():
    return urlMap


# request body should include long url to shorten and an optional short url
@app.post("/shorten_url")
def toShorten(url: schemas.longURL, short: Optional[schemas.shortURL] = None):
    
    # when no short url given, generate one
    if short == None:
        short = randomID()
        urlMap[short] = url.long_Url
        return { 'short_url' : short }
    else:
        # when short URL is given, check to see if it already exists
        if short.short_Url in urlMap:
            raise HTTPException(status_code=404, detail=f"Short url {short.short_Url} already exist, try another one.")
        urlMap[short.short_Url] = url.long_Url
        return { 'short_url': short.short_Url }
    

# url parems for redirect to long URL
@app.get("/redirect/{short_URL}")
def getLongUrl(short_URL: str):
    if short_URL not in urlMap: # check to see if short URL exist in our data
        raise HTTPException(status_code=404, detail=f"Short URL of {short_URL} doesn't exist.")
    return RedirectResponse(urlMap[short_URL])
