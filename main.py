import nextcord
from nextcord.ext import commands, tasks
import os
from nextcord import Interaction
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from sheets import sheet
from utils import *
from api_keys import *
from datetime import datetime
import asyncio
import schedule


# Test job for schedule-driver output
# This job will print to the new-test-channel
def print_job():
    print("test job print - alternate")
    #channel = bot.get_channel(1155482375422218250)
    #date_time = datetime.now()
    #print(channel)
    #channel.send(f"Sending alternate message @ {date_time}")

    #channel.send("alternate test")


schedule.every(10).seconds.do(print_job)


async def task():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


pending_bids = []

# Definition requirements to allow bot to interact appropriately in discord
# If anything needs to be updated (e.g. admin-only commands) this would be adjusted accordingly
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

# Bot line - runs the bot
bot = commands.Bot(command_prefix="!", intents=intents)


# Bot start function - prints out to terminal to aid debugging if debug_mode is true
# Also opens logging file appropriately
@bot.event
async def on_ready():
    bot.loop.create_task(task())
    # Date format to add to log file name (YYYYMMDD)
    date_now = datetime.now()
    date = date_now.strftime("%Y%m%d")
    time = date_now.strftime("%H:%M:%S")
    if debug_mode:
        print(f"{date_now} Bot connection commenced - test bot {ver}")
        print("------------------------------")

    # Check if logs directory exists, and create if it does not
    logs_dir_exists = os.path.exists(logs_dir)
    if not logs_dir_exists:
        os.makedirs(logs_dir)

    # Log file name = pre + date
    log_filename = log_filename_pre + date
    # Should produce a log file unique to each day - will need to factor in some sort of cleanup routine on the system (probably via cron)
    # So that only 1 week of log files are retained

    # Check if log file already exists, if so open as append; otherwise open to write
    if os.path.exists(log_filename):
        log_file = open(log_filename, 'a')
    else:
        log_file = open(log_filename, 'w')

    # Print opening line to log file
    print(f"Bot starting at {time}", file=log_file)

    # Testing bot capability to print out to server channel
    channel = bot.get_channel(1146212963758391409)
    await channel.send("Bot starting up! Please place your bids")


# Bot fail/disconnect function - prints out to terminal to aid debugging if debug_mode is true
# Report failure to log file
@bot.event
async def on_disconnect():
    # Date format to add to log file name (YYYYMMDD)
    date_now = datetime.now()
    date = date_now.strftime("%Y%m%d")
    time = date_now.strftime("%H:%M:%S")
    if debug_mode:
        print(f"{date_now} Bot connection failure - test bot {ver}")
        print("------------------------------")

    # Prefix to log file
    log_filename_pre = "./logs/bid_bot.log_"
    log_filename = log_filename_pre + date
    # Should produce a log file unique to each day - will need to factor in some sort of cleanup routine on the system (probably via cron)
    # So that only 1 week of log files are retained

    # Check if log file already exists, if so open as append; otherwise open to write
    if os.path.exists(log_filename):
        log_file = open(log_filename, 'a')
    else:
        log_file = open(log_filename, 'w')

    # Print opening line to log file
    print(f"Bot failed to connect, or disconnected abruptly, at {time}", file=log_file)


# Bot close function - prints out to terminal to aid debugging if debug_mode is true
# Report close to log file
@bot.event
async def on_close():
    # Date format to add to log file name (YYYYMMDD)
    date_now = datetime.now()
    date = date_now.strftime("%Y%m%d")
    time = date_now.strftime("%H:%M:%S")
    if debug_mode:
        print(f"{date_now} Bot closed - test bot {ver}")
        print("------------------------------")

    # Prefix to log file
    log_filename_pre = "./logs/bid_bot.log_"
    log_filename = log_filename_pre + date
    # Should produce a log file unique to each day - will need to factor in some sort of cleanup routine on the system (probably via cron)
    # So that only 1 week of log files are retained

    # Check if log file already exists, if so open as append; otherwise open to write
    if os.path.exists(log_filename):
        log_file = open(log_filename, 'a')
    else:
        log_file = open(log_filename, 'w')

    # Print opening line to log file
    print(f"Bot closed at {time}", file=log_file)


# Simple test command - remove prior to pushing production version
@bot.slash_command(guild_ids=[test_server_id], name="test", description="Slash commands test")
async def test(interaction: Interaction):
    await interaction.response.send_message("Hello, test please")

# Load relevant cogs to support bot
bot.load_extension("cogs.Bids")
bot.load_extension("cogs.Scheduler")

if __name__ == '__main__':
    print(pending_bids)
# Run bot from main
if __name__ == '__main__':
    bot.run(BOT_TOKEN)
