from tkinter.tix import MAX
from discord import Interaction, Message, app_commands
from discord.ext.commands import Cog

from bot import PluralKitDMUtilities
from utils.errors import FrontHistoryFetchFailed


MAX_SHOWN_FRONTERS: int = 4


class CheckCommand(Cog):
    def __init__(self, bot: PluralKitDMUtilities) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='❓ Check front for message',
            callback=self.check_front_for_message,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    @app_commands.allowed_contexts(dms=True, private_channels=True, guilds=True)
    @app_commands.allowed_installs(users=True, guilds=True)
    async def check_front_for_message(self, interaction: Interaction[PluralKitDMUtilities], message: Message) -> None:
        whitelist = await self.bot.service.get_user_whitelist(message.author.id)

        if (
            interaction.user.id not in whitelist
            and interaction.user.id != message.author.id
        ):
            return await interaction.response.send_message(
                content=f"This user either doesn't have a PK Utilities profile setup, or you are not whitelisted to see this users profile.",
                ephemeral=True,
            )

        try:
            recent_switches = await self.bot.service.get_front_at_time(message.author.id, time=message.created_at)
        except FrontHistoryFetchFailed as e:
            return await interaction.response.send_message(
                content=f"Uh oh, an error was raised while trying to fetch the front history: {e}",
                ephemeral=True,
            )

        if len(recent_switches) == 0:
            return await interaction.response.send_message(
                content=f"This message is from before PluralKit was being used by this user.",
                ephemeral=True,
            )

        front_ids = recent_switches[0]['members']

        fronters_formatted: list[str] = []
        for member_id in front_ids:
            if len(fronters_formatted) >= MAX_SHOWN_FRONTERS:
                continue
            member = await self.bot.service.get_member_information(message.author.id, member_id)
            fronters_formatted.append(f"[{member['display_name'] or member['name']}](https://pluralkit.xyz/m/{member_id})")
        extra = ""
        if len(fronters_formatted) > MAX_SHOWN_FRONTERS:
            extra = f" (+ {len(front_ids)-MAX_SHOWN_FRONTERS} more)"
        return await interaction.response.send_message(
            content=f"Fronters: {', '.join(fronters_formatted)}{extra}",
            ephemeral=True,
        )


async def setup(bot: PluralKitDMUtilities) -> None:
    await bot.add_cog(CheckCommand(bot))
