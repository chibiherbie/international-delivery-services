from src.config import settings
from src.connectors.redis_connector import RedisManager
from src.connectors.session_aiohttp import HTTPSession

redis_manager = RedisManager(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
)

session = HTTPSession()
