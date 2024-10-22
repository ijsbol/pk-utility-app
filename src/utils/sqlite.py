from sys import exit as sys_exit
from sqlite3 import Connection
from sqlite3 import Connection, Error
from sqlite3 import connect as sync_connect

from utils.env import DATABASE_NAME


__all__: tuple[str, ...] = (
    "sqlite_connection",
    "check_sqlite_connection",
)


sqlite_connection: bool | Connection = False


def check_sqlite_connection() -> None:
    try:
        sqlite_connection = sync_connect(DATABASE_NAME)
        cursor = sqlite_connection.cursor()
        print("Database created and Successfully Connected to SQLite")

        sqlite_select_query = "select sqlite_version();"
        cursor.execute(sqlite_select_query)
        record = cursor.fetchall()
        print(f"SQLite Database Version is: {record}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS UserConfig (
                discord_user_id     TEXT NOT NULL,
                pluralkit_token     TEXT,
                whitelist_mode      BOOLEAN NOT NULL
            );
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_discord_user_id
                ON UserConfig(discord_user_id);
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS UserWhitelist (
                whitelist_owner_user_id     TEXT NOT NULL,
                whitelisted_user_id         TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_whitelist_span
                ON UserWhitelist(whitelist_owner_user_id, whitelisted_user_id);
        """)

        cursor.close()
    except Error as error:
        print(f"[SQLite Error] Error while connecting to SQLite {error}")
        sys_exit(-1)
    except Exception as error:
        print(f"[Unknown Error] Error on DB loading: {error}")
        sys_exit(-1)
