import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.middleware.sessions import SessionMiddleware

sys.path.append(str(Path(__file__).parent.parent))

from src.tasks.scheduler import scheduler
from src.config import settings
from src.init import redis_manager, session
from src.api.packages import router as router_package
from src.api.debug import router as router_debug


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    session.start()
    scheduler.start()
    yield
    session.stop()
    await redis_manager.close()

app = FastAPI(lifespan=lifespan)

app.include_router(router_package)
app.include_router(router_debug)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)
