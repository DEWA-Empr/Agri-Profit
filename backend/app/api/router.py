from fastapi import APIRouter
from .endpoints import ledger, dss, equipment

api_router = APIRouter()
api_router.include_router(ledger.router)
api_router.include_router(dss.router)
api_router.include_router(equipment.router)
