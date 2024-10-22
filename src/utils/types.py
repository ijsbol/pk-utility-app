from typing import TypedDict


__all__: tuple[str, ...] = (
    "SwitchAPI",
)


class SwitchAPI(TypedDict):
    id: str
    timestamp: str
    members: list[str]
