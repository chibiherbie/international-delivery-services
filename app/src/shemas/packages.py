from pydantic import BaseModel, Field, condecimal, validator, field_validator


class PackageRequest(BaseModel):
    name: str
    weight: float = Field(..., gt=0, description="Вес посылки в кг")
    package_type_id: int
    cost_in_usd: condecimal(gt=0, max_digits=4, decimal_places=2) = Field(..., description="Стоимость в долларах")


class PackageAdd(PackageRequest):
    session_id: str


class PackageById(PackageRequest):
    delivery_cost: condecimal(gt=0, max_digits=4, decimal_places=2) | None | str = None

    @field_validator('delivery_cost', mode='before')
    def set_delivery_cost(cls, v):
        return v if v is not None else "Не рассчитано"


class Package(PackageById):
    id: int
    delivery_company: int | None = None


class PackageId(BaseModel):
    id: int


class PackageType(BaseModel):
    id: int
    name: str
