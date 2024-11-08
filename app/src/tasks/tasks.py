from decimal import Decimal

from src.api.dependecies import get_session
from src.models.packages import PackageOrm
from src.tasks.scheduler import scheduler
from src.utils.usdt import get_usd_to_rub


@scheduler.scheduled_job('interval', minutes=5)
def periodic_task():
    calculate_delivery_cost()
    print("Цены доставки обновлены.")


async def calculate_delivery_cost():
    db = get_session()
    packages: list = get_unprocessed_packages(db)

    usd_to_rub = await get_usd_to_rub()

    for package in packages:
        delivery_cost = (package.weight * Decimal('0.5') + package.cost_in_usd * Decimal('0.01')) * Decimal(usd_to_rub)
        update_package_delivery_cost(db, package, delivery_cost)


def get_unprocessed_packages(db):
    return db.query(PackageOrm).filter(PackageOrm.delivery_cost.is_(None)).all()


def update_package_delivery_cost(db, package, delivery_cost):
    package.delivery_cost = delivery_cost
    db.add(package)
    db.commit()
