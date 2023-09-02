import nextcord

from nextcord.ext import commands
from nextcord import Interaction
from apikeys import *


class Greetings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="hello", description="Hello introduction via slash commadn", guild_ids=[test_server_id])
    async def hello(self, interaction: Interaction):
        await interaction.response.send_message("Hello, subscribe please (command ran via cog)")

    @commands.Cog.listener()
    async def on_message(self, messaage):
        if messaage.author == self.bot.user:
            return

        if "bidding" in messaage.content:
            await messaage.channel.send("Are you trying to make a bid?")


def setup(bot):
    bot.add_cog(Greetings(bot))
