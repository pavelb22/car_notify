from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        time VARCHAR(255) NOT NULL,
        url_avito VARCHAR(255) NULL,
        flag_pay BOOLEAN,
        last_id_drom varchar(255)
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id, time, url_avito, flag_pay, last_id_drom):
        sql = "INSERT INTO users (full_name, username, telegram_id, time, url_avito, flag_pay, last_id_drom) " \
              "VALUES($1, $2, $3, $4, $5, $6, $7) returning *"
        return await self.execute(sql, full_name, username, telegram_id, time, url_avito, flag_pay, last_id_drom,
                                  fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def save_num_car(self, telegram_id):
        sql = 'UPDATE Users SET num_car=$1 WHERE telegram_id=$2'
        return await self.execute(sql, telegram_id, execute=True)

    async def delite_user(self, telegram_id):
        sql = 'DELETE FROM Users WHERE telegram_id=$1'
        return await self.execute(sql, telegram_id, execute=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def get_user_paid(self, flag_pay):
        sql = 'SELECT * FROM Users WHERE flag_pay=$1'
        return await self.execute(sql, flag_pay, fetch=True)

    async def update_last_id_drom(self, last_id_drom, telegram_id):
        sql = "UPDATE Users SET last_id_drom=$1 WHERE telegram_id=$2"
        return await self.execute(sql, last_id_drom, telegram_id, execute=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def update_url_avito(self, url_avito, telegram_id):
        sql = "UPDATE Users SET url_avito=$1 WHERE telegram_id=$2"
        return await self.execute(sql, url_avito, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)