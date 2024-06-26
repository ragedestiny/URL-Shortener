from fastapi import FastAPI
from apitally.fastapi import ApitallyMiddleware
import os
from dotenv import load_dotenv
load_dotenv()

from app.api.url_handlers import router as url_router
from app.api.user_handlers import router as user_router
from app.api.admin_handlers import router as admin_router
from app.service.redis_client import redis_client
from app.service.cache_population import populate_cache_from_database
from app.models.database import Urls


app = FastAPI()

apitally_client_id = os.getenv("APITALLY_CLIENT_ID")

app.add_middleware(
    ApitallyMiddleware,
    client_id=apitally_client_id,
    env="prod" if os.getenv("PRODUCTION") else "dev"
)

populate_cache_from_database(redis_client=redis_client, Urls=Urls)

# Mount routers
app.include_router(url_router, tags=["urls"])
app.include_router(user_router, tags=["users"])
app.include_router(admin_router, tags=["admins"])
