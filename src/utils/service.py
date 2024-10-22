from datetime import datetime
from enum import member
from http import HTTPStatus
from typing import TYPE_CHECKING

from sqlite3 import Row
from typing import Any, cast
from urllib import response

from aiohttp import ClientSession
from aiosqlite import connect as aio_connect
from discord.ext.commands import AutoShardedBot

from utils.env import DATABASE_NAME
from utils.errors import FrontHistoryFetchFailed
from utils.functions import format_timestamp, unix_to_rfc3399
from utils.types import SwitchAPI, UserConfig


type PluralKitDMUtilities = AutoShardedBot


if TYPE_CHECKING:
    from bot import PluralKitDMUtilities


__all__: tuple[str, ...] = (
    "Service",
)


class Service:
    __slots__: tuple[str, ...] = (
        'bot',
    )

    def __init__(self, bot: PluralKitDMUtilities) -> None:
        self.bot = bot

    async def get_member_information(self, user_id: int, member_id: str) -> ...:
        user_config = await self.get_user_config(user_id)
        if user_config is None:
            raise FrontHistoryFetchFailed("Requested user has no user config setup.")
        headers = {}
        if user_config['pluralkit_token'] is not None:
            headers = {'Authorization': user_config['pluralkit_token']}
        async with ClientSession(headers=headers, base_url="https://api.pluralkit.me") as session:
            async with session.get(url=f"/v2/members/{member_id}") as resp:
                response_json: list[SwitchAPI] | dict[str, Any] = await resp.json()
                if (
                    resp.status == HTTPStatus.UNAUTHORIZED
                    or (
                        type(response_json) == dict
                        and response_json.get('code', 0) == 30005
                    )
                ):
                    raise FrontHistoryFetchFailed("User has a private front history but no pluralkit token saved.")
                return cast(list[SwitchAPI], response_json)

    async def get_front_at_time(self, user_id: int, time: datetime) -> list[SwitchAPI]:
        user_config = await self.get_user_config(user_id)
        if user_config is None:
            raise FrontHistoryFetchFailed("Requested user has no user config setup.")
        headers = {}
        if user_config['pluralkit_token'] is not None:
            headers = {'Authorization': user_config['pluralkit_token']}
        async with ClientSession(headers=headers, base_url="https://api.pluralkit.me") as session:
            async with session.get(url=f"/v2/systems/{user_id}/switches", params={
                'limit': 1,
                'before': unix_to_rfc3399(time.timestamp()),
            }) as resp:
                response_json: list[SwitchAPI] | dict[str, Any] = await resp.json()
                if (
                    resp.status == HTTPStatus.UNAUTHORIZED
                    or (
                        type(response_json) == dict
                        and response_json.get('code', 0) == 30005
                    )
                ):
                    raise FrontHistoryFetchFailed("User has a private front history but no pluralkit token saved.")
                response_json = cast(list[SwitchAPI], response_json)
                return response_json

    async def get_user_config(self, user_id: int) -> UserConfig | None:
        query = """
            SELECT * FROM UserConfig
                WHERE discord_user_id=?
        """
        args = (str(user_id),)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            data = await (await db.execute(query, args)).fetchone()
            data = cast(dict[str, Any] | None, data)
            if data is None:
                return
        return UserConfig(
            discord_user_id=int(data['discord_user_id']),
            pluralkit_token=data['pluralkit_token'],
            whitelist_mode=data['whitelist_mode'],
        )

    async def create_user_config(self, user_id: int) -> None:
        query = """
            INSERT INTO UserConfig (
                discord_user_id,
                pluralkit_token,
                whitelist_mode
            ) VALUES (?, ?, ?)
        """
        args = (str(user_id), None, True)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            await db.execute_insert(query, args)
            await db.commit()

    async def delete_user_config(self, user_id: int) -> None:
        query = """
            DELETE FROM UserConfig
                WHERE discord_user_id = ?;
        """
        args = (user_id,)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            await db.execute_insert(query, args)
            await db.commit()

    async def get_user_whitelist(self, user_id: int) -> list[int]:
        query = """
            SELECT whitelisted_user_id FROM UserWhitelist
                WHERE whitelist_owner_user_id = ?
        """
        args = (user_id,)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            rows = await db.execute_fetchall(query, args)
            rows = cast(list[dict[str, str]] | None, rows)
            if rows is None:
                return []
        return [int(row['whitelisted_user_id']) for row in rows]

    async def add_user_to_whitelist(self, whitelist_owner_user_id: int, whitelisted_user_id: int) -> None:
        query = """
            INSERT INTO UserWhitelist (
                whitelist_owner_user_id,
                whitelisted_user_id,
            ) VALUES (?, ?)
        """
        args = (whitelist_owner_user_id, whitelisted_user_id)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            await db.execute_insert(query, args)
            await db.commit()

    async def remove_user_from_whitelist(self, whitelist_owner_user_id: int, whitelisted_user_id: int) -> None:
        query = """
            DELETE FROM UserWhitelist
                WHERE whitelist_owner_user_id=?
                    AND whitelisted_user_id=?
        """
        args = (whitelist_owner_user_id, whitelisted_user_id)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            await db.execute(query, args)
            await db.commit()

    async def set_whitelist_mode(self, user_id: int, whitelist: bool) -> None:
        query = """
            UPDATE UserWhitelist
                SET whitelist_mode=?
                WHERE discord_user_id=?
        """
        args = (whitelist, user_id)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            await db.execute(query, args)
            await db.commit()

    async def set_pluralkit_token(self, user_id: int, pluralkit_token: str | None) -> None:
        query = """
            UPDATE UserConfig
                SET pluralkit_token=?
                WHERE discord_user_id=?
        """
        args = (pluralkit_token, user_id)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            await db.execute(query, args)
            await db.commit()
