import os
# General utilities functions/definitions
debug_mode = True

data_dir = "./data/"
bid_close_filename = data_dir + "bid_close.tme"
logs_dir = "./logs/"
log_filename_pre = logs_dir + "bid_bot.log_"
bids_filename = data_dir + "bids.dat"


def bid_sort(bid_dict):

    print(bid_dict.items())
    sorted_dict = dict(sorted(bid_dict.items(), key=lambda x: x[1], reverse=True))

    return sorted_dict


# Converts all the values from bid dictionary to integers
# Required to enable the sorting function above
def bid_conv(bid_dict):
    for key in bid_dict.keys():
        tmp = bid_dict[key]
        int_tmp = int(tmp)
        bid_dict[key] = int_tmp

        return bid_dict


# Function to write bid out to bid datafile (will be called by both bid submission routines)
def bid_write(bid):
    # Check bid contains appropriate number of elements
    # Should contain player name, bid item, points of bid, time of bid, date of bid
    # If not, print message and return out of function
    elements = len(bid)
    if elements != 5:
        print(f"Attempting to write a bid with an incorrect number of elements - should contain 5 elements, instead contains {elements}")
        return False
    else:
        if debug_mode:
            print(f"Writing bid to file - {bid} to {bids_filename}")
    # Check if bid file exists, if not then create
    # If exists, then append latest bid as a new line
    if os.path.exists(bids_filename):
        for item in bid:
            print(item + "\t", file=open(bids_filename, 'a'))
    else:
        print("# Bids data", file=open(bids_filename, 'w'))
        for item in bid:
            print(item + "\t", file=open(bids_filename, 'a'))
    return True
