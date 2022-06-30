from fastapi import APIRouter
from app.api.routes import route_monitor



api_router = APIRouter()
api_router.include_router(route_monitor.router, prefix="/monitor", tags=["monitor"])