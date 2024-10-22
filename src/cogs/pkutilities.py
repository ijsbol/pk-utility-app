from discord import Interaction, app_commands
from discord.app_commands import AppCommandContext, AppInstallationType
from discord.ext.commands import Cog
from discord.utils import utcnow

from bot import PluralKitDMUtilities
from utils.errors import FrontHistoryFetchFailed


class PKUtilitiesCommand(Cog):
    def __init__(self, bot: PluralKitDMUtilities) -> None:
        self.bot = bot

    async def _verify_pk_utils_account(self, interaction: Interaction[PluralKitDMUtilities]) -> bool:
        user_config = await self.bot.service.get_user_config(interaction.user.id)
        if user_config is not None:
            await interaction.response.send_message(
                content="You already have a PK Utilities profile setup, please run `/pk-utilities delete` if you wish to delete it.",
                ephemeral=True,
            )
            return False
        return True

    pk_utilities = app_commands.Group(
        name="pk-utilities",
        description="Configure your PluralKit Utility account",
        allowed_contexts=AppCommandContext(guild=True, dm_channel=True, private_channel=True),
        allowed_installs=AppInstallationType(guild=True, user=True),
    )

    @pk_utilities.command(
        name="get-started",
        description="List all approved users on your whitelist.",
    )
    async def pk_utilities_get_started(self, interaction: Interaction[PluralKitDMUtilities]) -> None:
        if not await self._verify_pk_utils_account(interaction):
            return

        await self.bot.service.create_user_config(interaction.user.id)
        try:
            await self.bot.service.get_front_at_time(interaction.user.id, utcnow())
        except FrontHistoryFetchFailed:
            return await interaction.response.send_message(
                content="Your PK Utilities profile has been created!\n- Your front history is set to private, please use `/config pluralkit-token set`\n- Currently your PK Utilities front history is whitelist-only, you can change this (or add/remove people to your whitelist) with `/config whitelist`.",
                ephemeral=True,
            )
        return await interaction.response.send_message(
            content="Your PK Utilities profile has been created!\n- Currently your PK Utilities front history is whitelist-only, you can change this (or add/remove people to your whitelist) with `/config whitelist`.",
            ephemeral=True,
        )


async def setup(bot: PluralKitDMUtilities) -> None:
    await bot.add_cog(PKUtilitiesCommand(bot))
