import os
from dotenv import load_dotenv
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, ListAttribute, NumberAttribute

# load environment variables from .env
load_dotenv()

# Read and load credentials
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "us-east-1")

# Set AWS credentials for pynamodb
os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id
os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key


class Urls(Model):
    class Meta:
        table_name = "Short_URL-to-Long_URL"
        region = aws_region
        
    short_url = UnicodeAttribute(hash_key=True)
    long_url = UnicodeAttribute()
    creator_email = UnicodeAttribute(default='')


class Users(Model):
    class Meta:
        table_name = "Users-table"
        region = aws_region 

    email = UnicodeAttribute(hash_key=True)
    password_hash = UnicodeAttribute()
    is_admin = BooleanAttribute(default=False)
    url_limit = NumberAttribute(default=20)
    urls = ListAttribute(default=list)  # Store the short urls created by user