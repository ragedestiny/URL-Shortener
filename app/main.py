from dotenv import load_dotenv

from models.schemas import validateLongUrl, validateShortUrl
from api.api_handlers import toShorten

load_dotenv()


print('Enter a url to shorten:')
longurl = validateLongUrl(input())

print('Enter a short url (leave blank if not specified):')
shorturl = validateShortUrl(input())

toShorten(long_url=longurl, shorturl=shorturl)