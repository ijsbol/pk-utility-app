from datetime import datetime
from typing import cast

from discord import Interaction, Message, User, app_commands
from discord.ext.commands import Cog

from bot import PluralKitDMUtilities
from utils.constants import (
    PLURALKIT_API_ERROR_SYSTEM_FRONT_HISTORY_PRIVATE,
    PLURALKIT_API_ERROR_SYSTEM_NOT_FOUND,
)
from utils.functions import snowflake_to_timestamp
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

    async def _handle_check_command(self, interaction: Interaction[PluralKitDMUtilities], timestamp: datetime, author_id: int) -> None:
        whitelist = await self.bot.service.get_user_whitelist(author_id)
        whitelist.append(author_id)
        user_information = await self.bot.service.get_user_config(author_id)
        if (
            interaction.user.id not in whitelist
            and user_information is not None
            and user_information['whitelist_enabled'] == True
        ):
            await interaction.edit_original_response(content="You have not been whitelisted to see this systems front history.")
            return

        recent_switches = await self.bot.service.get_front_at_time(author_id, time=timestamp, skip_auth_headers=True)
        if type(recent_switches) == int:
            if recent_switches == PLURALKIT_API_ERROR_SYSTEM_FRONT_HISTORY_PRIVATE:
                recent_switches = await self.bot.service.get_front_at_time(author_id, time=timestamp, skip_auth_headers=False)
                if recent_switches == PLURALKIT_API_ERROR_SYSTEM_FRONT_HISTORY_PRIVATE:
                    await interaction.edit_original_response(content="This system's PluralKit front history is private and has not provided a PluralKit token to this app (`/config pk-token set`).")
                    return
            elif recent_switches == PLURALKIT_API_ERROR_SYSTEM_NOT_FOUND:
                await interaction.edit_original_response(content="This account is not registered as a system with PluralKit.")
                return
            else:
                await interaction.edit_original_response(content="An unknown error has occurred.")
                return

        recent_switches = cast(list[SwitchAPI], recent_switches)
        if len(recent_switches) == 0:
            await interaction.edit_original_response(
                content=f"This message was sent before the first switch registered by this system.",
            )
            return

        use_display_name = True
        if user_information is not None:
            use_display_name = user_information['prefer_display_names']
        front_ids = recent_switches[0]['members']
        fronters_formatted: list[str] = []
        for member_id in front_ids:
            if len(fronters_formatted) >= MAX_SHOWN_FRONTERS:
                continue
            member = await self.bot.service.get_member_information(author_id, member_id)
            if member is None:
                continue
            if (member.get('privacy', {}) or {}).get('visibility', 'public') == 'public':
                fronters_formatted.append(
                    f"[{(member['display_name'] or member['name']) if use_display_name else member['name']}](https://pluralkit.xyz/m/{member_id})"
                )
        extra = ""
        if len(fronters_formatted) > MAX_SHOWN_FRONTERS:
            extra = f" (+ {len(front_ids)-MAX_SHOWN_FRONTERS} more)"

        await interaction.edit_original_response(
            content=f"Fronters: {', '.join(fronters_formatted)}{extra}",
        )

    @app_commands.allowed_contexts(dms=True, private_channels=True, guilds=True)
    @app_commands.allowed_installs(users=True, guilds=True)
    async def check_front_for_message(self, interaction: Interaction[PluralKitDMUtilities], message: Message) -> None:
        await interaction.response.defer(ephemeral=True)
        await self._handle_check_command(interaction, message.created_at, message.author.id)

    @app_commands.command(name="check-front", description="Check a front by message URL!")
    @app_commands.allowed_contexts(dms=True, private_channels=True, guilds=True)
    @app_commands.allowed_installs(users=True, guilds=True)
    async def check_front_command(
        self,
        interaction: Interaction[PluralKitDMUtilities],
        user_mention: User,
        message_url: str,
        ephemeral: bool = True,
    ) -> None:
        await interaction.response.defer(ephemeral=ephemeral)
        timestamp = snowflake_to_timestamp(int(message_url.split("/")[-1]))
        await self._handle_check_command(interaction, timestamp, user_mention.id)


async def setup(bot: PluralKitDMUtilities) -> None:
    await bot.add_cog(CheckCommand(bot))
