import os
import redis
from dotenv import load_dotenv
load_dotenv()

import logging
import sys
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

redis_server = os.getenv("REDIS_SERVER")
redis_password = os.getenv("REDIS_PASSWORD")

logging.info(redis_server, redis_password)
redis_client = redis.StrictRedis(host=redis_server, port=6379, db=0, password=redis_password) 