import asyncio
import json
import os
from playwright.async_api import async_playwright, BrowserContext, Page, TimeoutError
from .console import *
from .env import *
from .proxy import Proxy

class Browser:
    def __init__(self, storage_state: str = None, is_json_string: bool = False, proxy: Proxy = None):
        self.headless = HIDDEN_MODE
        self.storage_state = storage_state
        self.is_json_string = is_json_string
        self.playwright = None
        self.browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.proxy: Proxy = proxy

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        proxy = await self.validate_proxy()
        self.browser = await self.playwright.chromium.launch(headless=self.headless, proxy=proxy, args=["--lang=en-US"])

        context_args = {
            "locale": "en-US"
        }
        if self.storage_state:
            if self.is_json_string:
                context_args["storage_state"] = json.loads(self.storage_state)
            elif os.path.exists(self.storage_state):
                context_args["storage_state"] = self.storage_state
            else:
                raise FileNotFoundError(f"Storage state not found: {self.storage_state}")

        self.context = await self.browser.new_context(**context_args)
        self.page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def goto(self, url: str):
        if not self.page:
            raise Exception("Browser not launched")
        await self.page.goto(url)


    async def save_storage_state(self, path: str = None) -> str:
        if not self.context:
            raise Exception("Context not initialized")
        state = await self.context.storage_state()
        if path:
            with open(path, "w") as f:
                json.dump(state, f)
            print(f"Save session in {path}")
        return json.dumps(state)
    
    async def validate_proxy(self):
        if isinstance(self.proxy, Proxy):
            return {
                'server': self.proxy.full_proxy
            }
    

async def safe_wait_for_selector(page: Page, selector: str, timeout: int = 5000, state: str = "attached") -> bool:
    try:        
        await page.wait_for_selector(selector, timeout=timeout, state=state)
        return True
    except TimeoutError:
        return False
    
async def wait_not_stability_selector(page: Page, selector: str, timeout: int = 5000, state: str = "attached") -> bool:
    try:
        if selector == "#account_name_text_field":
            if await safe_wait_for_selector(page, selector, timeout=timeout, state=state):
                return True
            else:
                attempt = 0
                while attempt <= 5:
                    await page.reload(wait_until="networkidle")
                    attempt += 1
        
        await page.safe_wait_for_selector(selector, timeout=timeout, state=state)
        return True

    except TimeoutError:
        return False
    

async def get_frame_with_text(page, text: str):
    for frame in page.frames:
        try:
            content = await frame.content()
            if text in content:
                return frame
        except Exception as e:
            print(e)
    return None