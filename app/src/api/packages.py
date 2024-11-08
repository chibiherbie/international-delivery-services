import uuid
from sqlite3 import IntegrityError

from fastapi import HTTPException, APIRouter, Request, Query, Response
from sqlalchemy import select, insert
from starlette import status

from fastapi_cache.decorator import cache
from src.api.dependecies import SessionDep, PaginationDep
from src.models.packages import PackageOrm, PackageTypeOrm
from src.shemas.packages import PackageCreate, Package, PackageId, PackageType

router = APIRouter(prefix="/package", tags=["Посылки"])


@router.get("/", summary="Получение всех посылок пользователя")
async def get_packages(
        db: SessionDep,
        pagination: PaginationDep,
        request: Request,
        response: Response,
        type_id: str | None = Query(None, description='Тип посылки'),
        has_delivery_cost: bool | None = Query(None, description='Стоимость доставки'),
) -> list[Package]:
    session_id = request.session.get("session_id", str(uuid.uuid4()))
    request.session["session_id"] = session_id

    filters = [(PackageOrm.session_id.is_(session_id))]
    if type_id:
        filters.append(PackageOrm.package_type_id.in_(type_id))
        # query = query.filter(Package.package_type_id == type_id)
    if has_delivery_cost is not None:
        filters.append(
            PackageOrm.delivery_cost.isnot(None) if has_delivery_cost else PackageOrm.delivery_cost.is_(None)
        )
        # query = query.filter(Package.delivery_cost.isnot(None) if has_delivery_cost else Package.delivery_cost.is_(None))

    query = (
        select(PackageOrm)
        .filter(*filters)
        .limit(pagination.per_page)
        .offset((pagination.page - 1) * pagination.per_page)
    )

    result = await db.execute(query)
    return [Package.model_validate(model, from_attributes=True) for model in result.scalars().all()]


@router.get("/{package_id}", summary="Получение посылки по id")
@cache(expire=30)
async def get_package(package_id: int, db: SessionDep) -> Package:
    query = (
        select(PackageOrm)
        .filter_by(id=package_id)
    )

    result = await db.execute(query)
    model = result.scalars().one_or_none()
    if not model:
        raise HTTPException(404)
    return Package.model_validate(model, from_attributes=True)


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Сделать ставку на событие")
async def register_package(db: SessionDep, request: Request, package: PackageCreate) -> PackageId:
    session_id = request.session.get("session_id", str(uuid.uuid4()))
    request.session["session_id"] = session_id

    add_data_stmt = insert(PackageOrm).values(**package.model_dump()).returning(PackageOrm)
    result = await db.execute(add_data_stmt)
    model = result.scalars().one()

    return PackageId(id=model.id)


@router.get('/package_types', summary="Получить список доступных событий")
@cache(expire=30)
async def get_active_events(db: SessionDep) -> list[PackageType]:
    query = (select(PackageTypeOrm))
    result = await db.execute(query)
    return [PackageType.model_validate(model, from_attributes=True) for model in result.scalars().all()]


@router.post("/assign_company/{package_id}")
def assign_company(package_id: int, company_id: int, db: SessionDep):
    try:
        package = db.query(PackageOrm).filter(PackageOrm.id == package_id).with_for_update().first()

        if not package:
            raise HTTPException(404)

        if package.company_id is not None:
            raise HTTPException(409)

        package.company_id = company_id
        db.commit()

        return {"status": "success"}

    except IntegrityError:
        db.rollback()
        raise HTTPException
