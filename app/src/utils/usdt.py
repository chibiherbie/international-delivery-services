import json

from src.config import settings
from src.init import redis_manager, session


async def get_usd_to_rub() -> float:
    cached_rate = await redis_manager.get('usd_to_rub')
    if cached_rate:
        return float(cached_rate)

    async with session.session.get(settings.CURRENCY_API_URL) as response:
        text_data = await response.text()
        data = json.loads(text_data)
        usd_to_rub = data['Valute']['USD']['Value']

    await redis_manager.set('usd_to_rub', usd_to_rub, expire=600)

    return usd_to_rub
