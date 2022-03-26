from discord import Interaction


async def is_owner(interaction: Interaction) -> bool:
	return await interaction.client.is_owner(interaction.user)