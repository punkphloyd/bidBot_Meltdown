import nextcord
from nextcord import Interaction


class BeheButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.drop = None

    @nextcord.ui.button(label="Defending Ring", style=nextcord.ButtonStyle.red)
    async def dring(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("Defending Ring", ephemeral=True)
        self.drop = 'Defending Ring'
        self.stop()

    @nextcord.ui.button(label="Pixie Ring", style=nextcord.ButtonStyle.red)
    async def pring(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("Pixie Ring", ephemeral=True)
        self.drop = 'Pixie Ring'
        self.stop()

    @nextcord.ui.button(label="E Legs", style=nextcord.ButtonStyle.red)
    async def elegs(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("E Legs", ephemeral=True)
        self.drop = 'E Legs'
        self.stop()

    @nextcord.ui.button(label="M Legs", style=nextcord.ButtonStyle.red)
    async def mlegs(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("M Legs", ephemeral=True)
        self.drop = 'M Legs'
        self.stop()

    @nextcord.ui.button(label="W Head", style=nextcord.ButtonStyle.red)
    async def whead(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("W Head", ephemeral=True)
        self.drop = 'W Head'
        self.stop()

    @nextcord.ui.button(label="A Feet", style=nextcord.ButtonStyle.red)
    async def afeet(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("A Feet", ephemeral=True)
        self.drop = 'A Feet'
        self.stop()
