from discord import Interaction
from discord.app_commands import AppCommandContext, AppInstallationType, Group
from discord.ext.commands import Cog

from bot import PluralKitDMUtilities


class PKTokenCommand(Cog):
    def __init__(self, bot: PluralKitDMUtilities) -> None:
        self.bot = bot

    config = Group(
        name="config",
        description="Setup your PK Utilities config",
        allowed_contexts=AppCommandContext(guild=True, dm_channel=True, private_channel=True),
        allowed_installs=AppInstallationType(guild=True, user=True),
    )

    pk_token = Group(
        parent=config,
        name="pk-token",
        description="Set/delete your PluralKit api token for systems who have a private front history.",
    )

    @pk_token.command(
        name="set",
        description="Set your PluralKit API token (if your front history is private).",
    )
    async def config_pluralkit_token_set(self, interaction: Interaction[PluralKitDMUtilities], pluralkit_token: str) -> None:
        await self.bot.service.set_pluralkit_token(interaction.user.id, pluralkit_token)
        return await interaction.response.send_message(
            content="Your PluralKit token has been saved!",
            ephemeral=True,
        )

    @pk_token.command(
        name="delete",
        description="Delete your pluralkit token (if your front history is public).",
    )
    async def config_pluralkit_token_delete(self, interaction: Interaction[PluralKitDMUtilities]) -> None:
        await self.bot.service.set_pluralkit_token(interaction.user.id, None)
        return await interaction.response.send_message(
            content="Your PluralKit token has been deleted!",
            ephemeral=True,
        )

    @config.command(
        name="set-prefer-display-name",
        description="Set your front display to prefer a members display name or not.",
    )
    async def config_set_prefer_dispaly_name(self, interaction: Interaction[PluralKitDMUtilities], use_display_names: bool) -> None:
        await self.bot.service.set_prefer_display_names(interaction.user.id, use_display_names)
        message = "Your front will now show members display names."
        if not use_display_names:
            message = "Your front will now show members names rather than display names."
        return await interaction.response.send_message(content=message, ephemeral=True)

async def setup(bot: PluralKitDMUtilities) -> None:
    await bot.add_cog(PKTokenCommand(bot))
