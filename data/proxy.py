import asyncio
from .console import Interface, ui
from .req import Request


class Proxy:
    def __init__(self, host: str, port: int, link: str, proxy_type = 'socks5://'):
        self.proxy_type = proxy_type
        self.host = host
        self.port = port
        self.link_change_ip = link
        self.full_proxy = f'{self.proxy_type}{self.host}:{self.port}'
        self.working = False
        self.last_ip = None
        self.errors = None

    def __repr__(self):
        print(f'This proxy {self.full_proxy} | {self.link_change_ip}')

    async def get_ip(self):
        async with Request(proxy = self.full_proxy) as rq:
            return await rq.get_ip()
        return

    async def swap_ip(self):
        with ui.console.status(f"[bold green]Swap proxy IP") as status:
            async with Request(proxy = None) as rq:
                return await rq.swap_ip(swap_link=self.link_change_ip)
        return 
    




class ProxyManager:
    def __init__(self, proxies: list[Proxy] = None):
        self.proxies = proxies

    async def get(self):
        for proxy in self.proxies:
            if proxy.working == False:
                proxy.working = True
                counter = 0
                while counter <= 5:
                    counter += 1
                    new_ip = await proxy.swap_ip()
                    if new_ip != proxy.last_ip:
                        proxy.last_ip = await proxy.swap_ip()
                        ui.print(f"🟢 Proxy selected: [magenta]{proxy.proxy_type}{proxy.host}:{proxy.port}[/] | {proxy.last_ip}")
                        return proxy
                    ui.print(f'[red]Errors swap proxy: {counter}[/]')
                proxy.errors += 1
                ui.print(f'[red]{proxy.full_proxy} Error swap ip[/]')


    async def drop(self, proxy: Proxy):
        proxy.working = False
        proxy.last_ip = await proxy.get_ip()
