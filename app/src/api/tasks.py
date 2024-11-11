from fastapi import APIRouter

from src.tasks.scheduler import scheduler
from src.tasks.tasks import periodic_task

router = APIRouter(prefix="/debug", tags=["Tasks"])


@router.post("/run-update-shipping-costs/")
async def run_update_shipping_costs():
    scheduler.add_job(periodic_task)
    return {"status": "ok"}
