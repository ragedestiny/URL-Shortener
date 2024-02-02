from pynamodb.models import Model
from pynamodb.attributes import (UnicodeAttribute)


class Urls(Model):
    class Meta:
        table_name = "Short_URL-to-Long_URL"
        
    short_url = UnicodeAttribute(hash_key=True)
    long_url = UnicodeAttribute()
