from pydantic import BaseModel, HttpUrl, field_validator, ValidationError
import re

class longURL(BaseModel):
    # long url must be valid URL with http or https
    url: HttpUrl


class shortURL(BaseModel):
    short_Url: str
    
    @field_validator('short_Url')
    def isValid(cls, s: str) -> str:
        # validate short URL
        if len(s) > 15 or len(s) < 10: # between 10-15 character long
            raise ValueError(f"shortUrl must be between 10-15 characters long, input is: {len(s)} characters long.")
        if not bool(re.match("^[A-Za-z0-9_-]*$", s)): 
            # only A-Z or a-z or 0-9 or - or _
            raise ValueError(f"shortUrl must only contains letters, nummbers, underscores and dashes.")
        return s
    
# used to valid user inputs later
def validateLongUrl(url):
    try:
        long_url = longURL(url=url)
        print(f"longURL: {long_url}")
        return long_url
    except ValidationError as e:
        print(e)
        
def validateShortUrl(url):
    try:
        if not url:
            return None
        short_url = shortURL(short_Url=url)
        print(f"shortURL: {short_url}")
        return short_url
    except ValidationError as e:
        print(e)