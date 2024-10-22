from datetime import datetime
from typing import Any


__all__: tuple[str, ...] = (
    "chunk_list",
    "format_timestamp",
    "unix_to_rfc3399",
)


def chunk_list(input_list: list[Any], n: int) -> list[list[Any]]:
    return [input_list[i:i + n] for i in range(0, len(input_list), n)]


def format_timestamp(datetime_str: str) -> datetime:
    return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))


def unix_to_rfc3399(unix_timestamp: float) -> str:
    dt = datetime.utcfromtimestamp(unix_timestamp)
    rfc3399_format = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    return rfc3399_format
