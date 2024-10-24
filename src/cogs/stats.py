from discord import Interaction, app_commands
from discord.ext.commands import Cog

from bot import PluralKitDMUtilities
from utils.functions import chunk_list


class SystemStats(Cog):
    def __init__(self, bot: PluralKitDMUtilities) -> None:
        self.bot = bot

    @app_commands.command(
        name="system-stats",
        description="See your system message stats",
    )
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def config_whitelist_add(self, interaction: Interaction[PluralKitDMUtilities], ephemeral: bool = True, page: int = 1) -> None:
        if page < 1:
            return await interaction.response.send_message(
                content="Page must be at least 1.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=ephemeral)
        members = await self.bot.service.get_system_member_information(interaction.user.id)
        user_information = await self.bot.service.get_user_config(interaction.user.id)
        use_display_name = True
        if user_information is not None:
            use_display_name = user_information['prefer_display_names']

        message_counts: list[int] = [mem['message_count'] or 0 for _, mem in members.items()]
        total_messages = sum(message_counts)
        max_messages_width: int = max([len(str(msg_count)) for msg_count in message_counts])
        content: dict[int, str] = {
            (mem['message_count'] or 0): (
                f"`[{mid}]` `{str(mem['message_count'] or 0).rjust(max_messages_width)} messages` "
                f"`{str(round(((mem['message_count'] or 0) / total_messages) * 100, 2)).rjust(5)}%` "
                f"{self.bot.service.format_member_name(mem, use_display_name)}"
            ) for mid, mem in members.items()
        }
        sorted_content = dict(sorted(content.items(), reverse=True))
        pages = chunk_list([v for _, v in sorted_content.items()], 30)

        if page > len(pages):
            return await interaction.response.send_message(
                content=f"You don't have that many pages, you only have {len(pages)} pages.",
                ephemeral=True,
            )

        sorted_content_as_string = '\n'.join(pages[page - 1])
        sorted_content_as_string += f"\n\n**Total message count: `{total_messages}`**"
        sorted_content_as_string += f"\n-# **Page {page} / {len(pages)}**"
        await interaction.edit_original_response(content=sorted_content_as_string)


async def setup(bot: PluralKitDMUtilities) -> None:
    await bot.add_cog(SystemStats(bot))
