from discord import Interaction
from discord.app_commands import AppCommandContext, AppInstallationType, Group
from discord.ext.commands import Cog

from bot import PluralKitDMUtilities


class PKTokenCommand(Cog):
    def __init__(self, bot: PluralKitDMUtilities) -> None:
        self.bot = bot

    pk_token = Group(
        name="pk-token",
        description="Set/delete your PluralKit api token for systems who have a private front history.",
        allowed_contexts=AppCommandContext(guild=True, dm_channel=True, private_channel=True),
        allowed_installs=AppInstallationType(guild=True, user=True),
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
        await self.bot.service.delete_pluralkit_token(interaction.user.id)
        return await interaction.response.send_message(
            content="Your PluralKit token has been deleted!",
            ephemeral=True,
        )


async def setup(bot: PluralKitDMUtilities) -> None:
    await bot.add_cog(PKTokenCommand(bot))
