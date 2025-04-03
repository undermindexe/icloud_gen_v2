import asyncio

from data.console import Interface, ui, ASK_ACTION
from data.account import Account, AccountManager
from data.db import Database
from data.browser import Browser
from data.service import *
from data.env import *



async def worker_import(acc: Account):
    await acc.save_account()

async def worker_generate(acc: AccountManager):
    while True:
        try:
            account = await acc.get()
            if account:
                if await account.login():
                    await account.generate_hme()
                    await acc.drop(account)
        except Exception as e:
            print(e)

async def get_task():
    try:
        s = ui.ask(
            f"{ASK_ACTION}")
        if s == "1":
            accounts = get_accounts_from_txt()
            tasks = [worker_import(i) for i in accounts]
            return tasks
        elif s == "2":
            accounts = await get_accounts()
            manager = AccountManager(accounts=accounts)
            task = [worker_generate(manager)]
            return task
        elif s == "3":
            return 
        else:
            raise ValueError
    except (KeyboardInterrupt, ValueError):
        return


async def main():
    try:
        tasks = await get_task()

        if isinstance(tasks, list):
            await asyncio.gather(*tasks, return_exceptions=False)
    finally:
        await Database.close_connection()
        ui.print('[bold green]Success END all task[/]')

if __name__ == '__main__':
    asyncio.run(main())