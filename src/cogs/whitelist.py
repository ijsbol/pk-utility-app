from discord import Interaction, User
from discord.app_commands import AppCommandContext, AppInstallationType, Group
from discord.ext.commands import Cog

from bot import PluralKitDMUtilities
from utils.functions import chunk_list


class WhitelistCommand(Cog):
    def __init__(self, bot: PluralKitDMUtilities) -> None:
        self.bot = bot

    whitelist = Group(
        name="whitelist",
        description="Configure who can and can't use PK Utilities on your messages.",
        allowed_contexts=AppCommandContext(guild=True, dm_channel=True, private_channel=True),
        allowed_installs=AppInstallationType(guild=True, user=True),
    )

    @whitelist.command(
        name="add",
        description="Allow someone to check your front (if front privacy is enabled).",
    )
    async def config_whitelist_add(self, interaction: Interaction[PluralKitDMUtilities], user: User) -> None:
        if interaction.user.id == user.id:
            return await interaction.response.send_message(
                content=f"You can't add your own account to the whitelist.",
                ephemeral=True,
            )

        whitelist = await self.bot.service.get_user_whitelist(interaction.user.id)
        if user.id in whitelist:
            return await interaction.response.send_message(
                content=f"{user.mention} is already on your whitelist!",
                ephemeral=True,
            )

        await self.bot.service.add_user_to_whitelist(interaction.user.id, user.id)
        return await interaction.response.send_message(
            content=f"{user.mention} has been added to your whitelist!",
            ephemeral=True,
        )

    @whitelist.command(
        name="remove",
        description="Revoke someones access to check your front (if front privacy is enabled).",
    )
    async def config_whitelist_remove(self, interaction: Interaction[PluralKitDMUtilities], user: User) -> None:
        if interaction.user.id == user.id:
            return await interaction.response.send_message(
                content=f"You can't remove your own account from the whitelist.",
                ephemeral=True,
            )

        whitelist = await self.bot.service.get_user_whitelist(interaction.user.id)
        if user.id not in whitelist:
            return await interaction.response.send_message(
                content=f"{user.mention} is not on your whitelist!",
                ephemeral=True,
            )

        await self.bot.service.remove_user_from_whitelist(interaction.user.id, user.id)
        return await interaction.response.send_message(
            content=f"{user.mention} has been removed from your whitelist!",
            ephemeral=True,
        )

    @whitelist.command(
        name="list",
        description="List all approved users on your whitelist.",
    )
    async def config_whitelist_list(self, interaction: Interaction[PluralKitDMUtilities], page: int = 1) -> None:
        if page < 1:
            return await interaction.response.send_message(
                content="Page must be at least 1.",
                ephemeral=True,
            )

        whitelist = await self.bot.service.get_user_whitelist(interaction.user.id)
        whitelist_formatted = [f'`{uid}` - <@{uid}>' for uid in whitelist]
        whitelist_chunked = chunk_list(whitelist_formatted, 50)

        if page > len(whitelist_chunked):
            return await interaction.response.send_message(
                content=f"You don't have that many pages, you only have {len(whitelist_chunked)} pages.",
                ephemeral=True,
            )

        whitelist_page = whitelist_chunked[page - 1]
        formatted = '\n'.join(whitelist_page)
        formatted += f"\n\n-# **Page {page} / {len(whitelist_chunked)}**"
        return await interaction.response.send_message(content=formatted, ephemeral=True)

    @whitelist.command(
        name="enable",
        description="Enable your whitelist.",
    )
    async def config_whitelist_enable(self, interaction: Interaction[PluralKitDMUtilities]) -> None:
        await self.bot.service.set_whitelist_enabled(interaction.user.id, True)
        await interaction.response.send_message(
            content="Your whitelist has been enabled, only approved users can see your front history using this app. You can add approved users by doing `/whitelist add`.",
            ephemeral=True,
        )

    @whitelist.command(
        name="disable",
        description="Disable your whitelist.",
    )
    async def config_whitelist_disable(self, interaction: Interaction[PluralKitDMUtilities]) -> None:
        await self.bot.service.set_whitelist_enabled(interaction.user.id, False)
        await interaction.response.send_message(
            content="Your whitelist has been disabled, anyone can now see your front history using this app.",
            ephemeral=True,
        )

async def setup(bot: PluralKitDMUtilities) -> None:
    await bot.add_cog(WhitelistCommand(bot))
