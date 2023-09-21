
debug_mode = True


def bid_sort(bid_dict):

    print(bid_dict.items())
    sorted_dict = dict(sorted(bid_dict.items(),key=lambda x: x[1], reverse=True))

    return sorted_dict


# Converts all the values from bid dictionary to integers
# Required to enable the sorting function above
def bid_conv(bid_dict):
    for key in bid_dict.keys():
        tmp = bid_dict[key]
        int_tmp = int(tmp)
        bid_dict[key] = int_tmp

        return bid_dict
