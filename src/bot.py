from discord import Intents
from discord.ext.commands import AutoShardedBot, when_mentioned

from utils.env import DISCORD_BOT_TOKEN
from utils.service import Service
from utils.sqlite import check_sqlite_connection


class PluralKitDMUtilities(AutoShardedBot):
    def __init__(self, intents: Intents, *args, **kwargs):
        super().__init__(intents=intents, command_prefix=when_mentioned, *args, **kwargs)
        self.service = Service(self)

    async def setup_hook(self):
        check_sqlite_connection()
        await self.load_extension('cogs.check')
        await self.load_extension('cogs.pk_token')
        await self.load_extension('cogs.whitelist')
        # await self.tree.sync()


intents = Intents.none()
bot = PluralKitDMUtilities(intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
