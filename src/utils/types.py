from typing import Literal, TypedDict


__all__: tuple[str, ...] = (
    "PRIVATE_TO_EVERYONE_INCL_SYSTEM",
    "PRIVATE_TO_EVERYONE_NOT_INCL_SYSTEM",
    "PUBLIC_TO_EVERYONE",
    "SwitchAPI",
    "FrontMemberVisibility",
)


PRIVATE_TO_EVERYONE_INCL_SYSTEM: Literal[0] = 0
PRIVATE_TO_EVERYONE_NOT_INCL_SYSTEM: Literal[1] = 1
PUBLIC_TO_EVERYONE: Literal[2] = 2


type FrontMemberVisibility = Literal[0, 1, 2]


class UserConfig(TypedDict):
    discord_user_id: str
    pluralkit_token: str
    whitelist_enabled: bool
    prefer_display_names: bool
    front_member_visibility: FrontMemberVisibility


class SwitchAPI(TypedDict):
    id: str
    timestamp: str
    members: list[str]
