from datetime import datetime, timezone

from .db import Database

class AccountRepository:

    @staticmethod
    async def add_account(email: str, password: str = None, user_agent: str = None, session: str = None):
        query = '''
        INSERT INTO Accounts (email, password, user_agent, session, created)
        VALUES(?,?,?,?,?)
        '''
        now = datetime.now(timezone.utc)
        await Database.execute(query, (email, password, user_agent, session, now))
    
    @staticmethod
    async def get_account_by_email(email: str):
        query = 'SELECT * FROM Accounts WHERE email = ?'
        return await Database.query_custom_row(query, (email,), one=True)
    
    @staticmethod
    async def get_all_accounts():
        query = 'SELECT * FROM Accounts'
        return await Database.query_custom_row(query)
    
    @staticmethod
    async def update_session(email: str, session: str):
        query = 'UPDATE Accounts SET session = ? WHERE email = ?'
        await Database.execute(query, (session, email))

    @staticmethod
    async def update_count_hme(email: str, count_hme: str):
        query = 'UPDATE Accounts SET count_hme = ? WHERE email = ?'
        await Database.execute(query, (count_hme, email))

    @staticmethod
    async def update_last_generate(email: str, last_generate):
        query = 'UPDATE Accounts SET last_generate = ? WHERE email = ?'
        await Database.execute(query, (last_generate, email))

    @staticmethod
    async def update_list_hme(email: str, list_hme):
        query = 'UPDATE Accounts SET list_hme = ? WHERE email = ?'
        await Database.execute(query, (list_hme, email))