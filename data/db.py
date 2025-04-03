import asyncio
import aiosqlite

class Database:
    _connection = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_connection(cls):
        if cls._connection is None:
            cls._connection = await aiosqlite.connect('database.db')
        await cls._connection.execute('PRAGMA journal_mode=WAL;')
        await cls._connection.commit()

        await cls._connection.execute('''
            CREATE TABLE IF NOT EXISTS Accounts(
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT,
            user_agent TEXT,
            session TEXT,
            last_generate DATETIME,
            count_hme TEXT,
            list_hme TEXT,
            created DATETIME
        )
        ''')
        await cls._connection.commit()

        await cls._connection.execute('''
            CREATE INDEX IF NOT EXISTS idx_email ON Accounts(email)
        ''')
        await cls._connection.commit()

        return cls._connection

    @classmethod
    async def execute(cls, query, params = ()):
        async with cls._lock:
            conn = await cls.get_connection()
            await conn.execute(query, params)
            await conn.commit()

    @classmethod
    async def executemany(cls, query, params = ()):
        async with cls._lock:
            conn = await cls.get_connection()
            await conn.executemany(query, params)
            await conn.commit()

    @classmethod
    async def query(cls, query, params = (), description = False):
        async with cls._lock:
            conn = await cls.get_connection()
            async with conn.execute(query, params) as cursor:
                result = await cursor.fetchall()
                if description:
                    return result, cursor.description
        return result
    
    @classmethod
    async def query_custom_row(cls, query, params = (), one = False):
        async with cls._lock:
            conn = await cls.get_connection()
            default_row_factory = conn.row_factory
            conn.row_factory = aiosqlite.Row
            if one:
                async with conn.execute(query, params) as cursor:
                    result = await cursor.fetchone()
            else:
                async with conn.execute(query, params) as cursor:
                    result = await cursor.fetchall()
            conn.row_factory = default_row_factory
        return result


    @classmethod
    async def close_connection(cls):
        if cls._connection:
            await cls._connection.close()
            cls._connection = None
