import datetime
import os
import random

from utils import debug_mode
from api_keys import *
from nextcord.ext import commands, tasks

# Define UTC (shouldn't matter really)
utc = datetime.timezone.utc

# Time for random bid close generation (i.e. midnight/0001)
bid_close_gener_time = datetime.time(hour=0, minute=1)

# Time for bid application & writing to spreadsheet (1900)
bid_application_time = datetime.time(hour=19, minute=0)


class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.apply_bids.start()
        self.generate_bid_close.start()
        if debug_mode:
            print(f"{bid_application_time} is the bid application time")
            print(f"{bid_close_gener_time} is the bid close time")

    def cog_unload(self):
        self.apply_bids.cancel()
        self.generate_bid_close.cancel()

    @tasks.loop(time=bid_close_gener_time)
    async def generate_bid_close(self):
        if debug_mode:
            print(f"It is {bid_close_gener_time}, the program will now generate a bid close time (selected randomly between 4pm and 7pm)")

        # Check if data directory exists, it not then create it
        data_dir = "./data/"
        data_dir_exists = os.path.exists(data_dir)
        if not data_dir_exists:
            os.makedirs(data_dir)

        # File to store random bid window close time, open as 'w' as we always want to overwrite previous content if any present
        bid_close_file = data_dir + "bid_close.tme"
        bc_file = open(bid_close_file, 'w')

        random_time = random.randint(0, 180)
        random_hour = int(random_time/60)
        random_min = (random_time - 60*random_hour)

        bid_close_hour = 16 + random_hour
        bid_close_minute = 0 + random_min

        print(f"{bid_close_hour}{bid_close_minute}", file=bc_file)

    @tasks.loop(time=bid_application_time)
    async def apply_bids(self):
        if debug_mode:
            print(f"It is {bid_application_time}, the program will now examine the day's bids and push valid bids to sheet")
        channel = self.bot.get_channel(bids_channel_id)
        await channel.send(f"Activating bids from today")

        # Check if data directory exists, it not then create it
        data_dir = "./data/"
        data_dir_exists = os.path.exists(data_dir)
        if not data_dir_exists:
            os.makedirs(data_dir)

        # Check bit deadline file exists, otherwise return an error
        bid_close_file = data_dir + "bid_close.tme"
        if os.path.exists(bid_close_file):
            bcf = open(bid_close_file, 'r')

        for line in bcf:
            if debug_mode:
                print(line)
            bid_ct = line

        if debug_mode:
            print(f"Bid close time is : {bid_ct}")

        bid_deadline = 0000
        await channel.send(f"Bid close time for today was {bid_deadline}")

# Function to run the cog within the bot
def setup(bot):
    bot.add_cog(Scheduler(bot))
