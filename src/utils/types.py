from typing import TypedDict


__all__: tuple[str, ...] = (
    "SwitchAPI",
)


class UserConfig(TypedDict):
    discord_user_id: str
    pluralkit_token: str
    whitelist_enabled: bool
    prefer_display_names: bool


class SwitchAPI(TypedDict):
    id: str
    timestamp: str
    members: list[str]
