from pydantic import BaseModel, HttpUrl, EmailStr, field_validator, ValidationError, Field
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
    
class Email(BaseModel):
    # email must be a valid email
    email: EmailStr


class Password(BaseModel):
    password: str
    
    @field_validator('password')
    def check_password(cls, value):
        # convert the password to a string if it is not already
        value = str(value)
        # check for blank spaces
        if " " in value:
            raise ValueError("Password cannot contain blank spaces.")
        # check that the password has at least 8 characters
        if len(value) < 8:
            raise ValueError("Password must have at least 8 characters.")
        # check if password has at least one uppercase letter
        if not any(c.isupper() for c in value):
            raise ValueError("Password must have at least one uppercase letter.")
        # check if password has at least one lowercase letter
        if not any(c.islower() for c in value):
            raise ValueError("Password must have at least one lowercase letter.")
        # check if password has at least one digit
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must have at least one digit.")
        
        return value

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
        
        
def validateEmail(email):
    try:
        new_email = Email(email=email)
        return new_email
    except ValidationError as e:
        raise ValueError(str(e))
    
def validatePassword(password):
    try:
        new_password = Password(password=password)
        return new_password
    except ValidationError as e:
        raise ValueError(str(e))