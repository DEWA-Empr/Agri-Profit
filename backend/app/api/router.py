from fastapi import APIRouter
from .endpoints import auth, ledger, dss, equipment, reports, investor

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(ledger.router)
api_router.include_router(dss.router)
api_router.include_router(equipment.router)
api_router.include_router(reports.router)
api_router.include_router(investor.router)
