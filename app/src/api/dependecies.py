from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 5


class PaginationParams(BaseModel):
    page: Annotated[int, Query(DEFAULT_PAGE, ge=1, description='Номер страницы откуда брать посылки')]
    per_page: Annotated[int | None, Query(DEFAULT_PER_PAGE, ge=1, le=100, description='Количество возвращенных посылок')]


PaginationDep = Annotated[PaginationParams, Depends()]


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
