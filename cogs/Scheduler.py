from datetime import datetime, time
import os
import random

from utils import debug_mode
from api_keys import *
from nextcord.ext import commands, tasks
from sheets import *
from utils import *

# Time for random bid close generation (i.e. midnight/0001)
bid_close_gener_time = time(hour=0, minute=1)

# Time for bid application & writing to spreadsheet (2350)
# This application time ensures bids will not be updated mid-event, and only 'take effect' the following day
bid_application_time = time(hour=23, minute=50)

# Two processes above (bid close time generation & bid application time) could probably be combined into a single time
# And managed via a single function
# TO DO: Consider amalgamation of these two functions


class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.apply_bids.start()         # Start the scheduler for time based functions
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
        # Generate appropriate log filename first
        date = datetime.now()
        date = date.strftime("%Y%m%d")
        log_filename = log_filename_pre + date

        if debug_mode:
            print(f"It is {bid_application_time}, the program will now examine the day's bids and push valid bids to sheet")
        channel = self.bot.get_channel(bids_channel_id)
        await channel.send(f"Activating bids from {date}")
        # Initialise bid close time (bid_ct) and bid close file (bcf) prior to definition / reading
        bid_ct = 0
        bcf = None
        # Check if data directory exists, it not then create it (should exist)
        data_dir_exists = os.path.exists(data_dir)
        if not data_dir_exists:
            if debug_mode:
                print(f"Data directory {data_dir} did not exist, creating now")
            os.makedirs(data_dir)

        # Check bit deadline file exists, otherwise return an error
        bid_close_file = data_dir + "bid_close.tme"
        if os.path.exists(bid_close_file):
            bcf = open(bid_close_file, 'r')
            print(f"{bid_close_file} opened for reading", file=open(log_filename, 'a'))
        else:
            if debug_mode:
                print(f"Bid close timestamp file {bid_close_file} does not exist")
            await channel.send("Bid close timestamp file could not be found - see logs for further information")
            print(f"Error - unable to find bid deadline file {bid_close_file}", file=open(log_filename, 'a'))
            return
        # Read contents of bid close file (should be single line containing a single timestamp)
        for line in bcf:
            if debug_mode:
                print(line)
            bid_ct = line
        bcf.close()

        print(f"Bid close time for {date}: {bid_ct}", file=open(log_filename, 'a'))

        if debug_mode:
            print(f"Bid close time is : {bid_ct}")
        await channel.send(f"Bid close time for today was {bid_ct}")

        # Bids reading and action routine
        # Get bids data file
        bids_data_file = data_dir + "/bids.dat"
        bdf = None
        if os.path.exists(bids_data_file):
            bdf = open(bids_data_file,'r')
        else:
            if debug_mode:
                print(f"Failed to open bids data file: {bids_data_file}")
            await channel.send("Bids data file could not be opened - please see logs for further details")
            print(f"{date}: {time} - Failed to open bid file: {bids_data_file}", file=open(log_filename, 'a'))
            return

        # Cycle through bids data file and check if bid is good or bad
        # If bid is good, apply it to google sheets and move to next bid
        # If bid is bad, respond accordingly

        for line in bdf:
            if debug_mode:
                print(line)
            bid = line
            # Check if bid contains correct number of line items
            if len(bid) != 6:
                if debug_mode:
                    print(f"Bid: {bid} should be 6 items in length. It is {len(bid)}")
                print(f"Bid: {bid} should be 6 items in length. It is {len(bid)}", file=open(log_filename, 'a'))
                continue
            # Check if bid is good using player, item, and points values
            bid_success, message_out = check_bid(bid[3],bid[4],bid[5])       
            if bid_success:
                await channel.send(f"Successful bid: {bid[3]} has bid {bid[5]} points on {bid[4]}")
                # Print success to log file
                print(f"{bid[2]} - Bid success: {bid_success} \n Message out: {message_out}", file=open(log_filename, 'a'))

                # Copy logic from previous (non time-delay) routine for writing to sheets
                # Get all existing bids on the corresponding item, and check if player already has an existing bid in place
                all_bids = get_all_bids(bid[4])
                if debug_mode:
                    print("Original bids: ")
                    print(all_bids)
                if bid[3] in all_bids.keys():
                    pre_bid = all_bids[bid[3]]

# Function to run the cog within the bot
def setup(bot):
    bot.add_cog(Scheduler(bot))
