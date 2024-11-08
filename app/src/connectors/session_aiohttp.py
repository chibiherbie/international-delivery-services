from typing import Optional
import aiohttp


class HTTPSession:
    _session: Optional[aiohttp.ClientSession] = None

    def start(self):
        self.session = aiohttp.ClientSession()
        return self.session

    async def stop(self):
        await self.session.close()
        self.session = None
