from datetime import datetime
from typing import Any


__all__: tuple[str, ...] = (
    "chunk_list",
    "format_timestamp",
    "unix_to_rfc3399",
    "snowflake_to_timestamp",
)


def chunk_list(input_list: list[Any], n: int) -> list[list[Any]]:
    return [input_list[i:i + n] for i in range(0, len(input_list), n)]


def format_timestamp(datetime_str: str) -> datetime:
    return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))


def unix_to_rfc3399(unix_timestamp: float) -> str:
    dt = datetime.utcfromtimestamp(unix_timestamp)
    rfc3399_format = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    return rfc3399_format


def snowflake_to_timestamp(snowflake: int) -> datetime:
    discord_epoch = 1420070400000  # Discord epoch in milliseconds (January 1, 2015)
    timestamp = ((snowflake >> 22) + discord_epoch) / 1000  # Shift right by 22 bits to get the time part, then add Discord's epoch
    return datetime.utcfromtimestamp(timestamp)
