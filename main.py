import nextcord
from nextcord.ext import commands
import os
from nextcord import Interaction
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from sheets import sheet
from utils import debug_mode
from apikeys import *
from datetime import date, time, datetime



intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

# Bot line - runs the bot
bot = commands.Bot(command_prefix="!", intents=intents)


# Bot start function - prints out to terminal to signify debugging if debug_mode is true
# Also opens logging file appropriately
@bot.event
async def on_ready():
    if debug_mode:
        print("Bot is ready - test bot {}".format(ver))
        print("------------------------------")
    
    # Prefix to log file 
    log_filename_pre = "./logs/bid_bot.log_"
    # Date format to add to log file (YYYYMMDD)
    date = datetime.now()
    date = date.strftime(%Y%m%d)
    log_filename = log_filename_pre + date
    
    # Check if log file already exists, if so open as append; otherwise open to write
    if os.path.exists(log_filename):
        log_file = open(log_filename, 'a')
    else:
        log_file = open(log_filename, 'w')

# Simple test command - remove prior to pushing production version
@bot.slash_command(guild_ids=[test_server_id], name="test", description="Slash commands test")
async def test(interaction: Interaction):
    await interaction.response.send_message("Hello, test please")

# Load relevant cogs to support bot
bot.load_extension("cogs.Bids")


# Run bot from main 
if __name__ == '__main__':
    bot.run(BOT_TOKEN)
