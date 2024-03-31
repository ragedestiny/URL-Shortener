from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
from starlette.responses import Response

from app.api.url_handlers import router as url_router
from app.api.user_handlers import router as user_router
from app.api.admin_handlers import router as admin_router

app = FastAPI()

# Prometheus metrics
request_counter = Counter('http_requests_total', 'Total HTTP Requests')

# Metrics route
@app.get("/metrics")
async def metrics():
    # Increment the request counter
    request_counter.inc()

    # Generate latest metrics in Prometheus format
    metrics_data = generate_latest()

    # Create a response object with metrics data
    response = Response(content=metrics_data)

    # Set content type to 'text/plain'
    response.headers['Content-Type'] = 'text/plain'

    return response

# Mount routers
app.include_router(url_router, tags=["urls"])
app.include_router(user_router, tags=["users"])
app.include_router(admin_router, tags=["admins"])