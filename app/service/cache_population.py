import os
from dotenv import load_dotenv
load_dotenv()

expiration_time = os.getenv("CACHE_EXPIRE_TIME")

def populate_cache_from_database(redis_client, Urls):
    """Populate the cache with existing short URLs from the database."""
    for url_pair in Urls.scan():
        redis_client.setex(url_pair.short_url, expiration_time, url_pair.long_url)
