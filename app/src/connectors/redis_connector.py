import redis.asyncio as redis


class RedisManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self):
        try:
            self.redis = await redis.Redis(host=self.host, port=self.port)
        except Exception as e:
            print(e)

    async def set(self, key: str, value: str, expire: int = None):
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
