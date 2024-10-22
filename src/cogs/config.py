from discord import Interaction, User, app_commands
from discord.app_commands import AppCommandContext, AppInstallationType
from discord.ext.commands import Cog

from bot import PluralKitDMUtilities
from utils.functions import chunk_list


class ConfigCommand(Cog):
    def __init__(self, bot: PluralKitDMUtilities) -> None:
        self.bot = bot

    async def _verify_pk_utils_account(self, interaction: Interaction[PluralKitDMUtilities]) -> bool:
        user_config = await self.bot.service.get_user_config(interaction.user.id)
        if user_config is None:
            await interaction.response.send_message(
                content="You don't have a PK Utilities profile setup, please run `/pk-utilities get-started`",
                ephemeral=True,
            )
            return False
        return True

    config = app_commands.Group(
        name="config",
        description="Configure your PluralKit Utility settings.",
        allowed_contexts=AppCommandContext(guild=True, dm_channel=True, private_channel=True),
        allowed_installs=AppInstallationType(guild=True, user=True),
    )

    config_pluralkit_token = app_commands.Group(
        parent=config,
        name="pluralkit-token",
        description="Set/remove your pluralkit token for systems who have a private front history."
    )

    @config_pluralkit_token.command(
        name="set",
        description="Set your pluralkit token (if your front history is private).",
    )
    async def config_pluralkit_token_set(self, interaction: Interaction[PluralKitDMUtilities], pluralkit_token: str) -> None:
        if not await self._verify_pk_utils_account(interaction):
            return

        await self.bot.service.set_pluralkit_token(interaction.user.id, pluralkit_token)
        return await interaction.response.send_message(
            content="Your pluralkit token has been saved!",
            ephemeral=True,
        )

    @config_pluralkit_token.command(
        name="delete",
        description="Delete your pluralkit token (if your front history is public).",
    )
    async def config_pluralkit_token_delete(self, interaction: Interaction[PluralKitDMUtilities]) -> None:
        if not await self._verify_pk_utils_account(interaction):
            return

        await self.bot.service.set_pluralkit_token(interaction.user.id, None)
        return await interaction.response.send_message(
            content="Your pluralkit token has been deleted!",
            ephemeral=True,
        )

    config_whitelist = app_commands.Group(
        parent=config,
        name="whitelist",
        description="Configure who can and can't use PK Utilities on your messages."
    )

    @config_whitelist.command(
        name="add",
        description="Allow someone to check your front via PK Utility (if whitelist is enabled).",
    )
    async def config_whitelist_add(self, interaction: Interaction[PluralKitDMUtilities], user: User) -> None:
        if not await self._verify_pk_utils_account(interaction):
            return

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

    @config_whitelist.command(
        name="remove",
        description="Revoke someones access to check your front via PK Utility (if whitelist is enabled).",
    )
    async def config_whitelist_remove(self, interaction: Interaction[PluralKitDMUtilities], user: User) -> None:
        if not await self._verify_pk_utils_account(interaction):
            return

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

    @config_whitelist.command(
        name="enable",
        description="Enable whitelist mode, only approved users can see your front via PK Utilities.",
    )
    async def config_whitelist_enable(self, interaction: Interaction[PluralKitDMUtilities]) -> None:
        if not await self._verify_pk_utils_account(interaction):
            return

        await self.bot.service.set_whitelist_mode(interaction.user.id, True)
        return await interaction.response.send_message(
            content="Your PK Utilities whitelist has been enabled (if previously disabled).",
            ephemeral=True,
        )

    @config_whitelist.command(
        name="disable",
        description="Disable whitelist mode, any user can see your front via PK Utilities.",
    )
    async def config_whitelist_disable(self, interaction: Interaction[PluralKitDMUtilities]) -> None:
        if not await self._verify_pk_utils_account(interaction):
            return

        await self.bot.service.set_whitelist_mode(interaction.user.id, False)
        return await interaction.response.send_message(
            content="Your PK Utilities whitelist has been disabled (if previously enabled).",
            ephemeral=True,
        )

    @config_whitelist.command(
        name="list",
        description="List all approved users on your whitelist.",
    )
    async def config_whitelist_list(self, interaction: Interaction[PluralKitDMUtilities], page: int = 1) -> None:
        if not await self._verify_pk_utils_account(interaction):
            return

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
        return await interaction.response.send_message(
            content='\n'.join(whitelist_page),
            ephemeral=True,
        )


async def setup(bot: PluralKitDMUtilities) -> None:
    await bot.add_cog(ConfigCommand(bot))
