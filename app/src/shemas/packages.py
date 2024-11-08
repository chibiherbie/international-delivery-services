from pydantic import BaseModel, Field, condecimal


class PackageCreate(BaseModel):
    name: str
    weight: float
    package_type_id: int
    cost_in_usd: condecimal(gt=0, max_digits=4, decimal_places=2) = Field(..., description="Стоимость в долларах")


class Package(PackageCreate):
    id: int
    delivery_company: int | None = None
    delivery_cost: condecimal(gt=0, max_digits=4, decimal_places=2) | None = None


class PackageId(BaseModel):
    id: int


class PackageType(BaseModel):
    id: int
    name: str
