import uuid
from sqlite3 import IntegrityError

from fastapi import HTTPException, APIRouter, Request, Query
from sqlalchemy import select, insert, update
from starlette import status

from fastapi_cache.decorator import cache
from src.api.dependecies import SessionDep, PaginationDep
from src.models.packages import PackageOrm, PackageTypeOrm
from src.shemas.packages import PackageRequest, Package, PackageId, PackageType, PackageAdd

router = APIRouter(prefix="/package", tags=["Посылки"])


@router.get('/package_types', summary="Получить список всех типов посылок")
@cache(expire=30)
async def get_active_events(db: SessionDep) -> list[PackageType]:
    query = (select(PackageTypeOrm))
    result = await db.execute(query)
    return [PackageType.model_validate(model, from_attributes=True) for model in result.scalars().all()]


@router.get("/", summary="Получение всех посылок пользователя")
async def get_packages(
        db: SessionDep,
        pagination: PaginationDep,
        request: Request,
        type_id: int | None = Query(None, description='Тип посылки'),
        has_delivery_cost: bool | None = Query(None, description='Стоимость доставки'),
) -> list[Package]:
    session_id = request.session.get("session_id", str(uuid.uuid4()))
    request.session["session_id"] = session_id

    filters = [(PackageOrm.session_id == session_id)]
    if type_id:
        filters.append(PackageOrm.package_type_id == type_id)
    if has_delivery_cost is not None:
        filters.append(
            PackageOrm.delivery_cost.isnot(None) if has_delivery_cost else PackageOrm.delivery_cost.is_(None)
        )

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
async def get_package(package_id: int, db: SessionDep) -> PackageRequest:
    query = (
        select(PackageOrm)
        .filter_by(id=package_id)
    )

    result = await db.execute(query)
    model = result.scalars().one_or_none()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Посылка не найдена")
    return PackageRequest.model_validate(model, from_attributes=True)


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Зарегистрировать посылку")
async def register_package(db: SessionDep, request: Request, package_data: PackageRequest) -> PackageId:

    query = select(PackageTypeOrm).filter_by(id=package_data.package_type_id).exists()
    result = await db.execute(select(query))
    if not result.scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Указанный тип посылки не найден"
        )

    session_id = request.session.get("session_id", str(uuid.uuid4()))
    request.session["session_id"] = session_id

    _package_data = PackageAdd(session_id=session_id, **package_data.model_dump())

    add_data_stmt = insert(PackageOrm).values(**_package_data.model_dump())
    result = await db.execute(add_data_stmt)
    await db.commit()

    package_id = result.lastrowid

    return PackageId(id=package_id)


@router.post("/assign_company/{package_id}")
async def assign_company(package_id: int, company_id: int, db: SessionDep):
    query = select(PackageOrm).where(PackageOrm.id == package_id)
    result = await db.execute(query)
    package = result.scalars().first()

    if not package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Посылка не найдена")

    update_query = (
        update(PackageOrm)
        .where(PackageOrm.id == package_id, PackageOrm.delivery_company.is_(None))
        .values(delivery_company=company_id)
        .execution_options(synchronize_session="fetch")
    )

    update_result = await db.execute(update_query)
    await db.commit()

    if update_result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Компания уже назначена")

    return {"status": "success"}
