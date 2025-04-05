from datetime import datetime, timezone
from pathlib import Path

from .proxy import Proxy
from .account import Account
from .console import Interface, ui
from .db import Database
from .account_respository import AccountRepository

def get_accounts_from_txt():
    try:
        with open('accounts.txt', 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]
            accounts = []
            for i in  lines:
                i = i.split(':')
                accounts.append(Account(email=i[0], password=i[1]))
            return accounts
            
    except Exception as e:
        print(e)


async def get_accounts():
    try:
        accounts = []
        result = [dict(row) for row in await AccountRepository.get_all_accounts()]
        rows = []
        for i in result:
            acc = Account()
            acc.__dict__.update(i)
            accounts.append(acc)
            rows.append([str(i['id']), 
                         i['email'], 
                         i['password'], 
                         i['last_generate'], 
                         i['count_hme'] if i['count_hme'] != None else 'None', 
                         i['created']])

        ui.print_table(title='[bold magenta]Accounts[/]', columns=['[bold green]id[/]', 
                                                                   '[bold blue]email[/]', 
                                                                   '[bold blue]password[/]', 
                                                                   '[bold blue]last generate[/]', 
                                                                   '[bold blue]count hide email[/]',
                                                                   '[bold blue]created[/]'], 
                                                                   rows=rows)
        return accounts
    except(TypeError) as e:
        print('The cookies.txt or proxy.txt file is likely empty')
        raise SystemExit
    
async def get_proxies():
    try:
        proxies = []
        with open('proxy.txt', 'r', encoding='utf-8') as file:
            line_proxies = [line.strip() for line in file.readlines() if line.strip()]
            for i in line_proxies:
                line = i.split(':')
                host = line[0]
                port = int(line[1])
                link = line[2] + ':' + line[3]
                proxies.append(Proxy(host = host, port = port, link = link, proxy_type = 'socks5://'))
        return proxies
    except(TypeError) as e:
        print(e)
        raise SystemExit

async def safe_wait_for_selector(page, selector: str, timeout: int = 5000, state: str = "visible") -> bool:
    try:
        await page.wait_for_selector(selector, timeout=timeout, state=state)
        return True
    except TimeoutError:
        return False
    