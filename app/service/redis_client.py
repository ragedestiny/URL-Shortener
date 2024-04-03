import os
import redis
from dotenv import load_dotenv
load_dotenv()

redis_server = os.getenv("REDIS_SERVER")
redis_password = os.getenv("REDIS_PASSWORD")

redis_client = redis.StrictRedis(host=redis_server, port=6379, db=0, password=redis_password) 