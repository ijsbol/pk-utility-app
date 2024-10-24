from discord import Intents
from discord.ext.commands import AutoShardedBot, Context, dm_only, when_mentioned

from utils.env import DISCORD_BOT_TOKEN, YOUR_DISCORD_USER_ID
from utils.service import Service
from utils.sqlite import check_sqlite_connection


class PluralKitDMUtilities(AutoShardedBot):
    def __init__(self, intents: Intents, *args, **kwargs):
        super().__init__(intents=intents, command_prefix=when_mentioned, *args, **kwargs)
        self.service = Service(self)

    async def setup_hook(self):
        check_sqlite_connection()
        await self.load_extension('cogs.check')
        await self.load_extension('cogs.config')
        await self.load_extension('cogs.whitelist')
        await self.load_extension('cogs.stats')


intents = Intents.none()
intents.dm_messages = True
bot = PluralKitDMUtilities(intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command(name="sync")
@dm_only()
async def sync_command(ctx: Context[PluralKitDMUtilities]) -> None:
    if ctx.author.id == YOUR_DISCORD_USER_ID:
        await bot.tree.sync()
        await ctx.reply("Synced!")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
