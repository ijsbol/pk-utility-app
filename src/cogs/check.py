from datetime import datetime, timedelta, timezone
from typing import cast

from discord import Interaction, Message, User, app_commands
from discord.ext.commands import Cog

from bot import PluralKitDMUtilities
from utils.constants import (
    PLURALKIT_API_ERROR_SYSTEM_FRONT_HISTORY_PRIVATE,
    PLURALKIT_API_ERROR_SYSTEM_NOT_FOUND,
)
from utils.functions import snowflake_to_timestamp
from utils.types import (
    PRIVATE_TO_EVERYONE_INCL_SYSTEM,
    PRIVATE_TO_EVERYONE_NOT_INCL_SYSTEM,
    PUBLIC_TO_EVERYONE,
    FrontMemberVisibility,
    SwitchAPI,
)


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

        front_member_visibility: FrontMemberVisibility = PRIVATE_TO_EVERYONE_NOT_INCL_SYSTEM
        if user_information is not None:
            front_member_visibility = user_information['front_member_visibility']

        show_private_members = (
            False if front_member_visibility == PRIVATE_TO_EVERYONE_INCL_SYSTEM
            else True if front_member_visibility == PRIVATE_TO_EVERYONE_NOT_INCL_SYSTEM and author_id == interaction.user.id
            else True if front_member_visibility == PUBLIC_TO_EVERYONE
            else False  # base case that should never be called lol
        )

        front_ids = recent_switches[0]['members']
        fronters_formatted: list[str] = []
        members = await self.bot.service.get_system_member_information(author_id)
        for member_id in front_ids:
            member = members.get(member_id, None)
            if member is None:
                continue
            member_is_private = not (member.get('privacy', {}) or {}).get('visibility', 'public') == 'public'
            if not member_is_private or member_is_private and show_private_members:
                fronters_formatted.append(
                    f"[{self.bot.service.format_member_name(member, use_display_name)}](https://pluralkit.xyz/m/{member_id})"
                )

        if len(front_ids) > 0:
            await interaction.edit_original_response(
                content=f"Fronters: {', '.join(fronters_formatted)}",
            )
            return
        await interaction.edit_original_response(
            content="There is no one currently fronting / registered as switched in for this system."
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
        message_url: str | None = None,
        ephemeral: bool = True,
    ) -> None:
        await interaction.response.defer(ephemeral=ephemeral)
        if message_url is not None:
            timestamp = snowflake_to_timestamp(int(message_url.split("/")[-1]))
        else:
            timestamp = datetime.now(tz=timezone.utc) - timedelta(seconds=1)  # 1 second offset to adjust for PK api
        await self._handle_check_command(interaction, timestamp, user_mention.id)


async def setup(bot: PluralKitDMUtilities) -> None:
    await bot.add_cog(CheckCommand(bot))
