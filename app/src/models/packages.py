from decimal import Decimal
from typing import List

from sqlalchemy import ForeignKey, DateTime, func, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class PackageOrm(Base):
    __tablename__ = "package"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    session_id: Mapped[str]
    weight: Mapped[float]
    cost_in_usd: Mapped[Decimal]
    delivery_cost: Mapped[Decimal | None] = mapped_column(default=None)
    delivery_company: Mapped[int | None] = mapped_column(default=None)
    package_type_id: Mapped[int] = mapped_column(ForeignKey('package_type.id'))


class PackageTypeOrm(Base):
    __tablename__ = "package_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
