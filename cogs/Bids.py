import nextcord
from apikeys import *
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ui import Select, View
from SkyGodButtons import *
from AreaButtons import *
from SeaGodButtons import *
from DynaButtons import *
from datetime import date, time, datetime
import time
from sheets import *
from utils import debug_mode, bid_sort, bid_conv
from main import log_filename


# BidButtons class - this defines the top level set of buttons with which users will be presented upon the /bid2 function
# Buttons for Sky / Sea / Dyna / Limbus / HNMs
# Future content can be added with additional buttons
class BidButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label="Sky", style=nextcord.ButtonStyle.red)
    async def sky_bids(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("Sky bids", ephemeral=True)
        self.value = "Sky"
        self.stop()

    @nextcord.ui.button(label="Sea", style=nextcord.ButtonStyle.grey)
    async def sea_bids(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("Sea bids", ephemeral=True)
        self.value = "Sea"
        self.stop()

    @nextcord.ui.button(label="Dynamis", style=nextcord.ButtonStyle.blurple)
    async def dyna_bids(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("Dynamis bids", ephemeral=True)
        self.value = "Dynamis"
        self.stop()

    @nextcord.ui.button(label="Limbus", style=nextcord.ButtonStyle.green)
    async def limbus_bids(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("Limbus bids", ephemeral=True)
        self.value = "Limbus"
        self.stop()

    @nextcord.ui.button(label="HNM", style=nextcord.ButtonStyle.red)
    async def hnm_bids(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_message("HNM bids", ephemeral=True)
        self.value = "HNM"
        self.stop()


# Bids class which contains the logic to implement bid functions either manual (/bid) or button-led (/bid2)
class Bids(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.pending_bids = []      # Presently unused functionality - will be used to implement time delay to bid processing (7 pm GMT for bid application)
        

#########################################  BID FUNCTION #########################################
    # Function to add user bids (manual input)
    # This requires users to add their character name, the item to be bid upon, and the number of points they wish to bid (or increase their existing bid)
    # Currently function is not intelligent enough to correct spelling errors etc, so user must specify item correctly
    # Does not currently implement a 7 pm bid activation protocol
    @nextcord.slash_command(name="bid", description="Bidbot bid function", guild_ids=[test_server_Id])
    async def bid(self, interaction: Interaction, player, item, points):
        if debug_mode:
            print("Bid Function Debugging")
        bid_time = datetime.now()               # Presently unused - will be possibly needed when 7 pm implementation comes in
        
        # Transform player and item to title case - matches google sheets
        player = player.title()                 
        item = item.title()
        points = int(points)
        # Perform bid validity test and respond accordingly
        bid_success, message_out = check_bid(player, item, points)
        
        # If successful, report in discord channel that player has successfully bid their points on the item
        if bid_success:
            await interaction.response.send_message(f"{player} has successfully placed a bid of {points} points on {item}")
            
            # Print success to log file
            print(f"{bid_time} - Bid success: {bid_success} \n Message out: {message_out}", file=open(log_filename, 'a'))
            ######### Note, when the bot is updated to include time-delayed bid application (either in accordance with the fixed 7 pm cut-off, or with the randomised time window) 
            ######### this is where the primary bid addition function will end. It will populate the array pending_bids and another function will pick up the pending bids at the appropriate time and apply them
            ######### Presently, however, the bid application code is below and part of this single function
        
            # Get dictionary containing all player-bid pairs
            # E.g., Fortitude Torque : Hammer bids 10, Shamrock	bids 7, and	Tasco bids 1
            # This produces a dictionary which looks like:
            # { 'Hammer': 10, 'Shamrock': 7, 'Tasco': 1 } 
            all_bids = get_all_bids(bid_item)
            if debug_mode:
                print("Original bids: ")
                print(all_bids)
            
            # Check if player has a bid already on this item
            # If player has already got a bid on this item, need to add the extra bid points to the existing bid entry
            # And then re-sort and update
            pre_points = get_player_bid(player, bid_item)
            
            if pre_points != 0:     # i.e., player has points already in this item
                new_points = int(bid_points) + int(pre_points)
                all_bids[player] = new_points
                if debug_mode:
                    print("Existing bids updated")
                    print(all_bids)
            else:                   # pre_points == 0 -> i.e. fresh bid on this item for this player
                # Fresh bid - add new bid to this dictionary
                all_bids[player] = bid_points
            
            # FUNCTIONALITY TO BE ADDED IN V0.2 
            # Add successful bid to pending bids list
            #bid_pending = [player, item, points]
            # self.pending_bids.append(bid_pending)
            
            # Get number of points user has in bids on the item in question
            pre_bids = get_player_bid(player, item)
        
        # Otherwise, report to the player that the bid has failed and identify the diagnosed cause
        else:
            await interaction.response.send_message(f"The attempt for {player} to bid {points} points on item {item} was unsuccessful\n {message_out}")
            # Print failure to log file
            print(f"{bid_time} - Bid success: {bid_success} \n Message out: {message_out}", file=open(log_filename, 'a'))



######################################### FUNCTION END ##########################################

###################################### REMOVE BID FUNCTION ######################################
        # Function for players to remove points from their bidded items
        # This can be limited to admins if required to prevent abuse
        # Presently not implemented due to change of strategy regarding bid removal arrangements
        # If this changes again this function will need to be completed
    @nextcord.slash_command(name="removebid", description="Bidbot remove bid function", guild_ids=[test_server_id])
    async def remove_bid(self, interaction: Interaction, user, item, points):
        print("Remove bid function debugging")
        await interaction.response.send_message(f"{user} is removing {points} points from the item: {item} ")
        
        # FUNCTION NEEDS TO BE COMPLETED IF REMOVING BID BECOMES AN OPTION

######################################### FUNCTION END ##########################################

###################################### BUTTON BID FUNCTION ######################################
    # This function is the button entry equivalent of the /bid function
    # Due to the button implementation it is quite cumbersome, if this can be refactored and simplified this should be considered
    # Use of this function requires the user's Discord Display Name to match that of their character on the google sheets (should be case insensitive - to be tested)
    # Currently (21/09/23) this would require Unholy, Zonero, Elensar, Annasion, Nuppy, Sanarau to change their display names  
    @nextcord.slash_command(name="bid2", description="Content for items to bid on", guild_ids=[test_server_id])
    async def bid_buttons(self, interaction: Interaction, bid_points):
        bid_time = datetime.now()                   # Get time of bid
        
        view = BidButtons()                         # Output for Sky/Sea etc. choice
        view2 = None                                # To be re-assigned later, pending initial EG Area choice
        view3 = None                                # To be re-assigned later, pending initial EG Area choice
        await interaction.response.send_message("Select the end game content for your item bid", view=view)
        await view.wait()


        player = interaction.user.display_name      # Get player name from discord user displayname
        if debug_mode:
            print(f"{bid_time.hour}{bidtime.minute} User running /bid2 is {player}")
        
        if view.value == None:
            if debug_mode:
                print("View value of none has been reached - this should not be encountered; please examine logs")
            print(f"{player} has attempted a bid at {datetime} which has produced a view.value == None result", file=open(log_filename,'a'))
        
        # Each option produces multiple sub-options; majority of code work below is arranging the button interface for users to access
        # User selects sky option in first button options
        elif view.value == 'Sky':
            if debug_mode:
                print("Sky has been selected")
            view2 = SkyButtons()
            await interaction.followup.send("Which sky boss would you like?", view=view2)
            await view2.wait()
            
            # User offered then choice of gods for bids
            if view2.god == 'Kirin':
                if debug_mode:
                    print("Kirin has been selected")
                view3 = KirinButtons()
                await interaction.followup.send("Which Kirin drops would you like to bid on?", view=view3)
                await view3.wait()
            elif view2.god == 'Genbu':
                if debug_mode:
                    print("Genbu has been selected")
                view3 = GenbuButtons()
                await interaction.followup.send("Which Genbu drops would you like to bid on?", view=view3)
                await view3.wait()
            elif view2.god == 'Byakko':
                if debug_mode:
                    print("Byakko has been selected")
                view3 = ByakkoButtons()
                await interaction.followup.send("Which Byakko drops would you like to bid on?", view=view3)
                await view3.wait()
            elif view2.god == 'Suzaku':
                if debug_mode:
                    print("Suzaku has been selected")
                view3 = SuzakuButtons()
                await interaction.followup.send("Which Suzaku drops would you like to bid on?", view=view3)
                await view3.wait()
            elif view2.god == 'Seiryu':
                if debug_mode:
                    print("Seiryu has been selected")
                view3 = SeiryuButtons()
                await interaction.followup.send("Which Seiryu drops would you like to bid on?", view=view3)
                await view3.wait()
        ###########################
        
        # User selects sea option in first button options
        elif view.value == 'Sea':
            if debug_mode:
                print("Sea has been selected")
            view2 = SeaButtons()
            await interaction.followup.send("Which sea boss would you like?", view=view2)
            await view2.wait()
            if view2.god == 'AV':
                if debug_mode:
                    print("AV has been selected")
                view3 = AVButtons()
                await interaction.followup.send("Which Absolute Virtue drops would you like to bid on?", view=view3)
                await view3.wait()

            if view2.god == 'Love':
                if debug_mode:
                    print("JoL has been selected")
                view3 = LoveButtons()
                await interaction.followup.send("Which Love drops would you like to bid on?", view=view3)
                await view3.wait()

            if view2.god == 'Justice':
                if debug_mode:
                    print("JoJ has been selected")
                view3 = JusticeButtons()
                await interaction.followup.send("Which Justice drops would you like to bid on?", view=view3)
                await view3.wait()

            if view2.god == 'Hope':
                if debug_mode:
                    print("JoH has been selected")
                view3 = HopeButtons()
                await interaction.followup.send("Which Hope drops would you like to bid on?", view=view3)
                await view3.wait()

            if view2.god == 'Prudence':
                if debug_mode:
                    print("JoP has been selected")
                view3 = PrudenceButtons()
                await interaction.followup.send("Which Prudence drops would you like to bid on?", view=view3)
                await view3.wait()

            if view2.god == 'Fortitude':
                if debug_mode:
                    print("JoFort has been selected")
                view3 = FortitudeButtons()
                await interaction.followup.send("Which Fortitude drops would you like to bid on?", view=view3)
                await view3.wait()

            if view2.god == 'Temperance':
                if debug_mode:
                    print("JoT has been selected")
                view3 = TemperanceButtons()
                await interaction.followup.send("Which Temperance drops would you like to bid on?", view=view3)
                await view3.wait()

            if view2.god == 'Faith':
                if debug_mode:
                    print("JoFaith has been selected")
                view3 = FaithButtons()
                await interaction.followup.send("Which Faith drops would you like to bid on?", view=view3)
                await view3.wait()

            if view2.god == 'Ix\'aern':
                if debug_mode:
                    print("Ixaerns has been selected")
                view3 = IxaernButtons()
                await interaction.followup.send("Which Ix'Aern drops would you like to bid on?", view=view3)
                await view3.wait()
        ###########################
        
        # User selects dynamis option in first button options
        # They are then offered choice of Dyna Lord vs Dyna Tav vs Job Relics
        # Dyna Lord / Tav implementation not properly coded yet
        # If user selects Job they are offered choice from Head-Feet, Acc, Head-1 - Feet-1
        # This is then combined to, e.g., BRD Feet, or MNK Head -1 this should then match up with the spreadsheet (once punk has updated spreadsheet accordingly)

        elif view.value == 'Dynamis':
            if debug_mode:
                print("Dynamis has been selected")
            view2 = DynaButtons()
            await interaction.followup.send("Which dynamis drops would you like to view?", view=view2)
            await view2.wait()
            
            # Not Dyna-Lord / Dyna-Tav == Relic pieces
            if not view2.god == 'Dynamis-Lord' and not view2.god == 'Dyna-Tav':
                if debug_mode:
                    print("Job relic has been selected")
                view3 = RelicButtons()
                await interaction.followup.send("Which relic piece would you like to view?", view=view3)
                await view3.wait()

                if debug_mode:
                    relic_drop = str(view2.god) + " " + str(view3.drop)
                    print(f"{relic_drop}")
            elif view2.god == 'Dynamis-Lord':       # If User selects Dyna Lord button, bring up dyna lord drops
                view3 = DynaLButtons()
            else:                                   # Else, only other option is Dyna-Tav - bring up dyna tav
                view3 = DynaTButtons()
        
        # For relic, bid item is concatenation of job and piece (e.g. MNK Legs / RDM Head -1)
        if view.value == 'Dynamis' and not view2.god == 'Dynamis-Lord' and not view2.god == 'Dyna-Tav':
            bid_item = str(view2.god) + " " + str(view3.drop)
        else:
            bid_item = view3.drop   # Has this been coded fully in DynaButtons.py? Need to check
        
        if debug_mode:
            print(f"{player} has bid {bid_points} points on item {view3.drop} at {bid_time}")
        
        # Print bid details to log file
        print(f"{player} has bid {bid_points} points on item {view3.drop} at {bid_time}", file=open(log_filename, 'a'))
        
        
        # Perform bid validity test and respond accordingly
        bid_success, message_out = check_bid(player, bid_item, bid_points)
         

        # This bid_points int conversion needs to take place after the above check_bid function
        # otherwise function hangs/fails due to lack of isnumeric() function in the int type
        bid_points = int(bid_points)
        
        if debug_mode:
            print(bid_success)
            print(message_out)

        print(f"{bid_time} - Bid success: {bid_success} \n Message out: {message_out}", file=open(log_filename, 'a'))
        
        ######### Note, when the bot is updated to include time-delayed bid application (either in accordance with the fixed 7 pm cut-off, or with the randomised time window) 
        ######### this is where the primary bid addition function will end. It will populate the array pending_bids and another function will pick up the pending bids at the appropriate time and apply them
        ######### Presently, however, the bid application code is below and part of this single function
        
        # Get dictionary containing all player-bid pairs
        # E.g., Fortitude Torque : Hammer bids 10, Shamrock	bids 7, and	Tasco bids 1
        # This produces a dictionary which looks like:
        # { 'Hammer': 10, 'Shamrock': 7, 'Tasco': 1 } 
        all_bids = get_all_bids(bid_item)
        if debug_mode:
            print("Original bids: ")
            print(all_bids)

        # Check if player has a bid already on this item
        # If player has already got a bid on this item, need to add the extra bid points to the existing bid entry
        # And then re-sort and update
        pre_points = get_player_bid(player, bid_item)
        if pre_points != 0:
            # Player already has points on this item, update dictionary value to reflect
            new_points = int(bid_points) + int(pre_points)
            all_bids[player] = new_points
            if debug_mode:
                print("Existing bid updated:")
                print(all_bids)
        else:
            # Add new bid to this dictionary
            all_bids[player] = bid_points

            if debug_mode:
                print("New bid added:")
                print(all_bids)

        # bid_conv function required to convert all points values into integer format (they are read from sheets as a string) - otherwise sort won't work
        all_bids = bid_conv(all_bids)
        # Sort bids dictionary by points bid
        all_bids = bid_sort(all_bids)

        if debug_mode:
            print("Sorted bids: ")
            print(all_bids)

        if debug_mode:
            # Printing out in debug mode to ensure that column and row being obtained is the one expected
            print("column/row for bid_item: ")
            col, row = find_cell(bid_item)
            print(f"{col}{row}")

            print("column/row for player: ")
            colp, rowp = find_cell(player)
            print(f"{colp}{rowp}")

        if debug_mode:
            print(f"Implementing new bids onto {bid_item}")
        
        print(f"Adding bids: {all_bids} onto {bid_item}", file=open(log_filename, 'a'))
        update_bids(bid_item, all_bids)

        if debug_mode:
            print("Bids implemented - hopefully")
        # If successful, report in discord channel that player has successfully bid their points on the item
        if bid_success:
            await interaction.response.send_message(f"{player} has successfully placed a bid of {bid_points} points on {bid_item}")
        # Otherwise, report to the player that the bid has failed and identify the diagnosed cause
        else:
            await interaction.response.send_message(f"The attempt for {player} to bid {bid_points} points on item {bid_item} was unsuccessful\n {message_out}")

        

######################################### FUNCTION END ##########################################
    