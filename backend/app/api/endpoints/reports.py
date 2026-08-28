from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ...models import models
from ...models.database import get_db
from ...schemas import schemas
from ...services import reports_service
from ...core.roles import Permission
from ..deps import require

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/pnl", response_model=schemas.PnlReport)
def get_pnl(db: Session = Depends(get_db), current_user: models.User = Depends(require(Permission.FINANCE_READ))):
    return reports_service.get_pnl_report(db, current_user.farm_id)


@router.get("/pnl/monthly", response_model=List[schemas.MonthlyPnlPoint])
def get_monthly_pnl(db: Session = Depends(get_db), current_user: models.User = Depends(require(Permission.FINANCE_READ))):
    return reports_service.get_monthly_pnl(db, current_user.farm_id)


@router.get("/pnl.csv")
def get_pnl_csv(db: Session = Depends(get_db), current_user: models.User = Depends(require(Permission.FINANCE_READ))):
    csv_content = reports_service.generate_pnl_csv(db, current_user.farm_id)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="agriprofit_pnl_report.csv"'},
    )
