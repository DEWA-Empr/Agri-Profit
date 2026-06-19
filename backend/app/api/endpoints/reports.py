from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ...models.database import get_db
from ...schemas import schemas
from ...services import reports_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/pnl", response_model=schemas.PnlReport)
def get_pnl(db: Session = Depends(get_db)):
    return reports_service.get_pnl_report(db)


@router.get("/pnl.csv")
def get_pnl_csv(db: Session = Depends(get_db)):
    csv_content = reports_service.generate_pnl_csv(db)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="agriprofit_pnl_report.csv"'},
    )
