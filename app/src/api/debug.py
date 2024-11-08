from fastapi import APIRouter

from src.tasks.scheduler import scheduler
from src.tasks.tasks import calculate_delivery_cost

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.post("/run-update-shipping-costs/")
def run_update_shipping_costs():
    scheduler.add_task(calculate_delivery_cost)
    return {"status": "ok"}
