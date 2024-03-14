from fastapi import FastAPI
from app.api.url_handlers import router as url_router
from app.api.user_handlers import router as user_router
from app.api.admin_handlers import router as admin_router

app = FastAPI()

# Mount routers
app.include_router(url_router, tags=["urls"])
app.include_router(user_router, tags=["users"])
app.include_router(admin_router, tags=["admins"])