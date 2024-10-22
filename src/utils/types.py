from typing import TypedDict


__all__: tuple[str, ...] = (
    "UserConfig",
    "SwitchAPI",
)


class UserConfig(TypedDict):
    discord_user_id: int
    pluralkit_token: str | None
    whitelist_mode: bool


class SwitchAPI(TypedDict):
    id: str
    timestamp: str
    members: list[str]
