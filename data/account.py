import asyncio
from datetime import datetime, timezone

from .console import Interface, ui
from .account_respository import AccountRepository
from .browser import *
from .proxy import Proxy

class Account:
    def __init__(self, 
                 email: str = None,
                 password: str = None, 
                 user_agent: str = None, 
                 session: str = None, 
                 last_generate: datetime = None, 
                 count_hme: int = None, 
                 created: datetime = None):
        self.email = email
        self.password = password
        self.user_agent = user_agent
        self.session = session
        self.last_generate = last_generate,
        self.count_hme = count_hme,
        self.created = created,
        self.working = False
    
    async def save_account(self):
        if not await AccountRepository.get_account_by_email(self.email):
            await AccountRepository.add_account(
                email=self.email,
                password=self.password,
                user_agent=self.user_agent,
                session=self.session
            )
            ui.print(f'[bold green]Success collect account[/] {self.email}:{self.password}')
        else:
            ui.print(f'[bold red]The account is already in the database[/] {self.email}:{self.password}')

    async def update_session(self):
        await AccountRepository.update_session(email=self.email, session=self.session)
        ui.print(f'[bold magenta]Session has been updated[/] {self.email}')

    async def update_count_hme(self):
        await AccountRepository.update_count_hme(email=self.email, count_hme=self.count_hme)
        ui.print(f'[bold magenta]Count hiden email has been updated[/] {self.email}')
    
    async def update_last_generate(self):
        await AccountRepository.update_last_generate(email=self.email, last_generate=self.last_generate)
        ui.print(f'[bold magenta]Last generate time has been updated[/] {self.email}')

    async def login(self, proxy: Proxy = None):
        async with Browser(storage_state=self.session, is_json_string = True, proxy=proxy) as browser:
            attempt = 0
            while attempt <= 5:
                attempt += 1
                await browser.goto("https://www.icloud.com/icloudplus/")

                try:
                    if await safe_wait_for_selector(page=browser.page, selector="text='Sign In'", timeout=5000):
                        ui.print(f'[bold red]Need login in account[/] {self.email}:{self.password}')
                        await browser.page.click("text='Sign In'")
                        await asyncio.sleep(3)

                        iframe_login = await browser.page.wait_for_selector("#aid-auth-widget-iFrame")
                        frame = await iframe_login.content_frame()

                        if await safe_wait_for_selector(page = frame, selector="#account_name_text_field", timeout=20000):
                            await frame.fill("#account_name_text_field", self.email)
                            await frame.click("#sign-in") 
                            await frame.wait_for_selector("#password_text_field")
                            await frame.fill("#password_text_field", self.password)
                            await frame.click("#sign-in")
                            if await safe_wait_for_selector(frame, "text='Two-Factor Authentication'", timeout=10000):
                                await frame.fill('[aria-label="Enter Verification Code Digit 1"]', ui.ask(f'[bold green]Need Two-Factor Authentication:[/] {self.email}'))
                                await asyncio.sleep(5)
                                frame_privacy =  await get_frame_with_text(page=browser.page, text='Apple\u00A0Account & Privacy')
                                if frame_privacy:
                                    if await frame_privacy.wait_for_selector('button:has-text("Continue")', timeout=1000):
                                        await frame_privacy.click('button:has-text("Continue")')
                                if await frame.wait_for_selector("text='Trust this browser?'"):
                                    await frame.click("text='Trust'")
                                    if await browser.page.wait_for_selector("text='iCloud+ Features'", timeout=10000):
                                        ui.print(f'[bold green]Account success login[/] {self.email}')
                                        self.session = await browser.save_storage_state()
                                        await self.update_session()
                                        return True
                            elif await browser.page.wait_for_selector("text='iCloud+ Features'", timeout=10000):
                                ui.print(f'[bold green]Account success login[/] {self.email}')
                                self.session = await browser.save_storage_state()
                                await self.update_session()
                                return True
                    else:
                        ui.print(f'[bold green]Session validate[/] {self.email}:{self.password}')
                        self.session = await browser.save_storage_state()
                        await self.update_session()
                        return True
                    await asyncio.sleep(6000)
                except Exception as e:
                    print(e)
            return False

    async def generate_hme(self, proxy: Proxy = None):
        async with Browser(storage_state=self.session, is_json_string = True, proxy=proxy) as browser:
            await browser.goto("https://www.icloud.com/icloudplus/")

            try:
                if await safe_wait_for_selector(page=browser.page, selector="text='iCloud+ Features'", timeout=5000):
                    await browser.page.click('[aria-label="Show more options for Hide My Email"]')
                    counter = 0
                    while counter <= 7:
                        counter += 1
                        iframe_generator = await browser.page.wait_for_selector("iframe.child-application")
                        frame = await iframe_generator.content_frame()

                        if await safe_wait_for_selector(frame, 'h3.card-title:has-text("Set up a new email address")', timeout=4000):
                            title = await frame.wait_for_selector('h3.card-title:has-text("Set up a new email address")')
                            add_button = await title.evaluate_handle(
                            """el => el.closest('.card')?.querySelector('button[title="Add"]')""")
                            await add_button.click()
                        else:
                            if await safe_wait_for_selector(frame, 'button[title="Add"]', timeout=5000):
                                count_hme = await frame.text_content(".Typography.PanelTitle-title3.modal-subtitle")
                                self.count_hme = count_hme.rstrip(' active')
                                await self.update_count_hme()
                                ui.print(f'[bold magenta]Total hide email[/]: {self.count_hme} - {self.email}')

                                await frame.wait_for_selector('button[title="Add"]', timeout=5000)
                                await frame.click('button[title="Add"]')
                                await asyncio.sleep(1)

                        await frame.wait_for_selector('input[name="hme-label"]', timeout=5000)
                        await frame.fill('input[name="hme-label"]', '.')
                        await frame.fill('textarea[name="hme-note"]', 'I Love Expanse Crypto\nhttps://t.me/expanse_crypto')
                        await frame.click('text="Create email address"')
                        await asyncio.sleep(3)
                        if await frame.query_selector('.form-message'):
                            ui.print(f'[bold green]Hide email rate limit. Wait 60+ min[/] {self.email}')
                            break
                        await frame.click('text="Back"')
                        await asyncio.sleep(1)
                    return True
                else:
                    ui.print(f'[bold green]Session not valid[/] {self.email}:{self.password}')
                    return False
            except Exception as e:
                print(e)
                return False
            
class AccountManager:
    def __init__(self, accounts: list[Account] = None):
        self.accounts = accounts

    async def get(self):
        for acc in self.accounts:
            if acc.count_hme:
                acc.count_hme = int(acc.count_hme)
                if acc.count_hme < 750 and acc.working == False and validate_time(acc.last_generate) if acc.last_generate != None else True:
                    acc.working = True
                    ui.print(f"🟢 Account selected: [blue]{acc.email}[/]")
                    return acc
        with ui.console.status(f"[bold green]No available accounts. Waiting for 5 minutes") as status:
            counter = 600
            while counter >= 0:
                status.update(f"[bold magenta]No available accounts[/]. Waiting for [bold blue]{counter}[/] second")
                await asyncio.sleep(1)
                counter -= 1


    async def drop(self, account: Account):
        account.working = False
        account.last_generate = datetime.now(timezone.utc)
        await account.update_last_generate()


def validate_time(last_time):
    if last_time == None:
        return True
    if isinstance(last_time, str):
        last_time = datetime.fromisoformat(last_time)
    delta = datetime.now(timezone.utc) - last_time
    if delta.total_seconds() >= 60*60:
        return True