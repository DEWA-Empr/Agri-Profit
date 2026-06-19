from fastapi import APIRouter
from .endpoints import ledger, dss, equipment, reports

api_router = APIRouter()
api_router.include_router(ledger.router)
api_router.include_router(dss.router)
api_router.include_router(equipment.router)
api_router.include_router(reports.router)
