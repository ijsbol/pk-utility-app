
from os import getenv

from dotenv import load_dotenv


load_dotenv()


__all__: tuple[str, ...] = (
    "DISCORD_BOT_TOKEN",
    "DATABASE_NAME",
)


def _get_boolean(key: str, *, default: bool = False) -> bool:
    value = getenv(key)
    if value is None or value == "null":
        return default
    return value.lower() == "true"


def _get_int(key: str) -> int:
    value = getenv(key)
    if value is None or value == "null":
        return 0
    return int(value)


def _get_optional_int(key: str) -> int | None:
    value = getenv(key)
    if value is None or value == "null":
        return None
    return int(value)


def _get_str(key: str) -> str:
    value = getenv(key)
    assert value is not None
    return value


def _get_optional_str(key: str) -> str | None:
    value = getenv(key)
    if value is None or value == "null":
        return None
    return str(value)


DISCORD_BOT_TOKEN: str = _get_str("DISCORD_BOT_TOKEN")
DATABASE_NAME: str = _get_str("DATABASE_NAME") + ".db"
