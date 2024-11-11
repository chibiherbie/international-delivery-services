from decimal import Decimal

from sqlalchemy import select

from src.api.dependecies import get_session
from src.models.packages import PackageOrm
from src.tasks.scheduler import scheduler
from src.utils.usdt import get_usd_to_rub


@scheduler.scheduled_job('interval', minutes=5)
async def periodic_task():
    await calculate_delivery_cost()
    print("Цены доставки обновлены.")


async def calculate_delivery_cost():
    async for db in get_session():
        packages: list = await get_unprocessed_packages(db)

        usd_to_rub = Decimal(await get_usd_to_rub())

        for package in packages:
            delivery_cost = (Decimal(package.weight) * Decimal('0.5') + package.cost_in_usd * Decimal('0.01')) * usd_to_rub
            delivery_cost = delivery_cost.quantize(Decimal("0.01"))
            await update_package_delivery_cost(db, package, delivery_cost)


async def get_unprocessed_packages(db):
    res = await db.execute(select(PackageOrm).filter(PackageOrm.delivery_cost.is_(None)))
    return res.scalars().all()


async def update_package_delivery_cost(db, package, delivery_cost):
    package.delivery_cost = delivery_cost
    db.add(package)
    await db.commit()
