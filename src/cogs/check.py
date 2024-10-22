from typing import cast

from discord import Interaction, Message, app_commands
from discord.ext.commands import Cog

from bot import PluralKitDMUtilities
from utils.constants import (
    PLURALKIT_API_ERROR_SYSTEM_FRONT_HISTORY_PRIVATE,
    PLURALKIT_API_ERROR_SYSTEM_NOT_FOUND,
)
from utils.types import SwitchAPI


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
        await interaction.response.defer(ephemeral=True)

        whitelist = await self.bot.service.get_user_whitelist(message.author.id)
        whitelist.append(message.author.id)
        recent_switches = await self.bot.service.get_front_at_time(message.author.id, time=message.created_at, skip_auth_headers=True)
        if type(recent_switches) == int:
            if recent_switches == PLURALKIT_API_ERROR_SYSTEM_FRONT_HISTORY_PRIVATE and interaction.user.id in whitelist:
                recent_switches = await self.bot.service.get_front_at_time(message.author.id, time=message.created_at, skip_auth_headers=False)
                if recent_switches == PLURALKIT_API_ERROR_SYSTEM_FRONT_HISTORY_PRIVATE:
                    await interaction.edit_original_response(content="This system's PluralKit front history is private and has not provided a PluralKit token to this app (`/pk-token set`).")
                    return
            elif recent_switches == PLURALKIT_API_ERROR_SYSTEM_FRONT_HISTORY_PRIVATE and not interaction.user.id in whitelist:
                await interaction.edit_original_response(content="You have not been whitelisted to see this systems front history.")
                return
            elif recent_switches == PLURALKIT_API_ERROR_SYSTEM_NOT_FOUND:
                await interaction.edit_original_response(content="This account is not registered as a system with PluralKit.")
                return
            else:
                await interaction.edit_original_response(content="An unknown error has occoured.")
                return

        recent_switches = cast(list[SwitchAPI], recent_switches)
        if len(recent_switches) == 0:
            await interaction.edit_original_response(
                content=f"This message was sent before the first switch registered by this system.",
            )
            return

        front_ids = recent_switches[0]['members']

        fronters_formatted: list[str] = []
        for member_id in front_ids:
            if len(fronters_formatted) >= MAX_SHOWN_FRONTERS:
                continue
            member = await self.bot.service.get_member_information(message.author.id, member_id)
            if member.get('privacy', {}).get('visibility', 'public') == 'public':
                fronters_formatted.append(
                    f"[{member['display_name'] or member['name']}](https://pluralkit.xyz/m/{member_id})"
                )
        extra = ""
        if len(fronters_formatted) > MAX_SHOWN_FRONTERS:
            extra = f" (+ {len(front_ids)-MAX_SHOWN_FRONTERS} more)"

        await interaction.edit_original_response(
            content=f"Fronters: {', '.join(fronters_formatted)}{extra}",
        )


async def setup(bot: PluralKitDMUtilities) -> None:
    await bot.add_cog(CheckCommand(bot))
