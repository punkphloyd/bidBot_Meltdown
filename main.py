import nextcord
from nextcord.ext import commands
import os
from nextcord import Interaction

from apikeys import *

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)




@bot.event
async def on_ready():
    print("Bot is ready - test bot {}".format(ver))
    print("------------------------------")




bot.run(BOT_TOKEN)
