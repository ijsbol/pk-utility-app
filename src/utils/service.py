from datetime import datetime
from typing import TYPE_CHECKING

from sqlite3 import Row
from typing import Any, cast

from aiohttp import ClientSession
from aiosqlite import connect as aio_connect
from discord.ext.commands import AutoShardedBot

from utils.env import DATABASE_NAME
from utils.functions import unix_to_rfc3399
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

    async def __fetch_pk_api_headers(self, user_id: int) -> dict[str, str]:
        user_token = await self.get_user_config(user_id)
        if user_token is not None and user_token['pluralkit_token'] is not None:
            return {'Authorization': user_token['pluralkit_token']}
        return {}

    async def get_member_information(self, user_id: int, member_id: str) -> dict[str, Any]:
        headers = await self.__fetch_pk_api_headers(user_id)
        async with ClientSession(headers=headers, base_url="https://api.pluralkit.me") as session:
            async with session.get(url=f"/v2/members/{member_id}") as resp:
                return await resp.json()

    async def get_front_at_time(self, user_id: int, time: datetime, *, skip_auth_headers: bool) -> list[SwitchAPI] | int:
        headers = {}
        if not skip_auth_headers:
            headers = await self.__fetch_pk_api_headers(user_id)
        async with ClientSession(headers=headers, base_url="https://api.pluralkit.me") as session:
            async with session.get(
                url=f"/v2/systems/{user_id}/switches",
                params={
                    'limit': 1,
                    'before': unix_to_rfc3399(time.timestamp()),
                },
            ) as resp:
                response_json: list[SwitchAPI] | dict[str, Any] = await resp.json()
                if type(response_json) == dict:
                    return int(response_json["code"])
                return cast(list[SwitchAPI], response_json)

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
                whitelisted_user_id
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

    async def set_whitelist_enabled(self, user_id: int, whitelist_enabled: bool) -> None:
        query = """
            INSERT INTO UserConfig (
                discord_user_id,
                pluralkit_token,
                whitelist_enabled,
                prefer_display_names
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT(discord_user_id)
                DO UPDATE SET whitelist_enabled=?;
        """
        args = (user_id, None, whitelist_enabled, True, whitelist_enabled)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            await db.execute(query, args)
            await db.commit()

    async def set_prefer_display_names(self, user_id: int, prefer_display_names: bool) -> None:
        query = """
            INSERT INTO UserConfig (
                discord_user_id,
                pluralkit_token,
                whitelist_enabled,
                prefer_display_names
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT(discord_user_id)
                DO UPDATE SET prefer_display_names=?;
        """
        args = (user_id, None, True, prefer_display_names, prefer_display_names)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            await db.execute(query, args)
            await db.commit()

    async def set_pluralkit_token(self, user_id: int, pluralkit_token: str | None) -> None:
        query = """
            INSERT INTO UserConfig (
                discord_user_id,
                pluralkit_token,
                whitelist_enabled,
                prefer_display_names
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT(discord_user_id)
                DO UPDATE SET pluralkit_token=?;
        """
        args = (user_id, pluralkit_token, True, True, pluralkit_token)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            await db.execute(query, args)
            await db.commit()

    async def get_user_config(self, user_id: int) -> UserConfig | None:
        query = """
            SELECT * FROM UserConfig
                WHERE discord_user_id=?
        """
        args = (str(user_id),)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            return cast(
                UserConfig | None,
                (await (await db.execute(query, args)).fetchone())
            )

    async def delete_config(self, user_id: int) -> None:
        query = """
            DELETE FROM UserConfig
                WHERE discord_user_id=?
        """
        args = (str(user_id),)
        async with aio_connect(DATABASE_NAME) as db:
            db.row_factory = Row
            await db.execute(query, args)
            await db.commit()
