from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from apikeys import *
import functools
from utils import debug_mode

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()
roster_sheet = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Roster!A1:T50").execute()
roster_values = roster_sheet.get('values', [])
bid_sheet = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Bids!A1:AT500").execute()
bid_values = bid_sheet.get('values', [])

event_sheet = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Event Tracker!A1:BJ50").execute()
event_values = event_sheet.get('values', [])

points_sheet = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Points!A1:F50").execute()
points_values = points_sheet.get('values', [])


# Function to check that the player bidding is present on the roster
def check_roster(player):
    player_present = False
    for rows in roster_values:
        if rows:
            if rows[0] == player:
                player_present = True
                break

    return player_present


# Check if item is present on the bids list
def check_item(item):
    item_present = False
    for rows in bid_values:
        if rows:
            if rows[0] == item:
                item_present = True
                break

    return item_present


# Check that a player has a sufficient number of points to place their bid
def check_points(player, points):
    has_points = False
    player_points = 0
    for rows in points_values:
        if rows:
            if rows[0] == player:
                if int(rows[4]) >= int(points):
                    has_points = True
                    print(f"{player} has  {rows[4]} points, this is greater than the {points} required - SUCCESS")
                    break
                else:
                    has_points = False
                    print(f"{player} does not have at least {points} points; they only have {rows[4]} points - FAIL")
    return has_points


# Single function to carry out all checks and collect any errors accordingly
def check_bid(player, item, points):

    bid_success = False
    # Check if player exists in roster, otherwise failed bid
    player_present = check_roster(player)
    if player_present:
        # If player exists in roster, check item exists in biddable sheet, otherwise failed bid
        item_present = check_item(item)
        if item_present:
            # If player and item exist, check that bid is valid
            # (i.e. a whole integer >= 1 and the player has sufficient points), otherwise failed bid
            valid_points = points.isnumeric()
            has_points = check_points(player, points)
            if valid_points and has_points:
                if debug_mode:
                    print("All conditions met for bid - SUCCESS")
                    bid_success = True
                    valid_bid = "Bid successful"
                    return bid_success, valid_bid
            else:
                if not valid_points:
                    points_not_valid = "You did not enter an acceptable input for points, please only enter integers greater than or equal to one"
                    bid_success = False
                    return bid_success, points_not_valid
                elif not has_points:
                    points_not_present = f"{player} does not have at least {points} points to fulfill this bid"
                    bid_success = False
                    return bid_success, points_not_present

        else:
            item_not_present = f"{item} is not present on the biddable items list"
            bid_success = False
            return bid_success, item_not_present
    else:
        player_not_present = f"{player} is not present on the roster"
        bid_success = False
        return bid_success, player_not_present


# Function to return the existing number of points bid by a player on an item (if any)
def get_player_bid(player, item):
    pre_bid = 0
    all_bids = get_all_bids(item)
    if player in all_bids.keys():
        pre_bid = all_bids[player]
        if debug_mode:
            print("Player has a bid")

    return pre_bid


# Function to return all the bids against any item in pairs of "Player: Bid", held in a dictionary
# Keys = Player Names
# Values = Points
# If empty, return None
def get_all_bids(item):
    all_bids = {}
    for rows in bid_values:
        if rows[0] == item:
            if len(rows) == 1:
                return None
            else:
                bid_pairs_len = len(rows) - 1
                for i in range(1,bid_pairs_len+1,2):
                    all_bids[rows[i]] = int(rows[i+1])

    return all_bids


# Function which will work out the cell ID (e.g., B7) for the given text
# Should only be used for item labels (possibly player labels also, but with caution)
# For items in bids and players on roster this should always be column 'A'
# However function is kept generic to allow for future requirements
def find_cell(text):
    not_item = False
    not_player = False
    row_num = 1
    col_num = 1
    # Check items
    for row in bid_values:
        if text in row:
            col_num = row.index(text) + 1
            break
        row_num = row_num + 1
        if row == bid_values[len(bid_values)-1]:
            not_item = True

    if not_item:
        row_num = 1
        col_num = 1
        for row in roster_values:
            if text in row:
                col_num = row.index(text) + 1
                break
            row_num = row_num + 1
            if row == roster_values[len(roster_values)-1]:
                not_player = True

    # if the result cannot be found in either items list or players list then simply return 0, 0
    # Can consider implementing further error catch/response later - but this should (in theory) never be encountered...
    if not_item and not_player:
        return 0, 0
    else:
        col_num = chr(ord('@')+col_num)
        return col_num, row_num


# This function updates the array of bids to reflect the new bid
# Needs to
def update_bids(item, dicto):

    # Find cell for item
    col, row = find_cell(item)
    updated_cell = str(col) + str(row)

    if col != 'A':
        if debug_mode:
            print("Column is not A - should this be A?")
    else:
        # Cell to begin inserting updated bids from
        updated_cell = "B"+str(row)
        if debug_mode:
            print(f"Updated cell: {updated_cell}")

    # Convert dictionary to list to update spreadsheet
    # List needs to be 2-d to work with 'request' line below
    bid_list = [list(functools.reduce(lambda x, y: x + y, dicto.items()))]

    #
    if debug_mode:
        print("Printing bid_list")
        print(bid_list)

    # Execute request for spreadsheet update
    #
    request = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Bids!{updated_cell}", valueInputOption="RAW", body={"values": bid_list}).execute()

    return


