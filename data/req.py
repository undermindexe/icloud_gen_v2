import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector

class Request:

    def __init__(self, proxy: str = ""):
        self.proxy = proxy
        self.headers={
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Content-Type": "text/plain",
            "Accept": "*/*",
            "Sec-GPC": "1",
            "Origin": "https://google.com",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://google.com",
            "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8,cs;q=0.7"
        }

    async def __aenter__(self):
        if self.proxy != None and self.proxy.startswith("socks5://"):
            connector = ProxyConnector.from_url(self.proxy)
        elif self.proxy:
            connector = aiohttp.TCPConnector()
        else:
            connector = aiohttp.TCPConnector()

        self.s = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=10),
            connector=connector
        )
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        await self.s.close()

    async def get_ip(self):
        try:
            async with self.s.get(f"https://api.ipify.org?format=json") as resp:
                last_ip = await resp.json()
                return last_ip['ip']
        except asyncio.TimeoutError:
            return {"error": 1, "reason": "Request timed out"}
        except Exception as e:
            return {"error": 1, "reason": str(e)}

    async def swap_ip(self, swap_link):
        try:
            url = f"{swap_link}&format=json"
            async with self.s.get(url, timeout=30) as resp:
                res = await resp.json()
                return res['new_ip']
        except asyncio.TimeoutError:
            return {"error": 1, "reason": "Request timed out"}
        except Exception as e:
            return {"error": 1, "reason": str(e)}