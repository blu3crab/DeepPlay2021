###############################################################################
# BleCheck - check various attributes & features of BleHealthSnapshots
#
# getMillis --get current milliseconds
# getIntervalGap --get upload interval gap between snapshots
# isTimeOrdered --descending, most recent to least recent
###############################################################################
import json
import time

import BleHealthSnapshot as bleHealthSnapshot

###############################################################################
# getMillis --get current milliseconds
def getMillis():
    # local time!
    # dt = datetime.now()
    # ms = (dt.day * 24 * 60 * 60 + dt.second) * 1000 + dt.microsecond / 1000
    # print(dt.date(), ", ms ", ms)

    # get UTC milliseconds
    ms = int(round(time.time() * 1000))
    # print("getMillis: UTC ",ms, " ms")
    return ms

###############################################################################
# getIntervalGap --get upload interval gap between snapshots
def getIntervalGap(currentTimeMs, prevTimeMs):
    interval_gap = (currentTimeMs - prevTimeMs) / bleHealthSnapshot.BleHealthSnapshot.DURATION_IDEAL_MS
    return interval_gap

###############################################################################
# isTimeOrdered --descending, most recent to least recent
TIME_TICKER_LABEL = bleHealthSnapshot.TIME_TICKER_LABEL
PHONE_MOBILE_ID = bleHealthSnapshot.PHONE_MOBILE_ID
TX_NAME_LABEL = bleHealthSnapshot.TX_NAME_LABEL
def isTimeOrdered(jsonObj, prevJsonObj):
    try:
        # extract keep alive ticker
        time_ticker = jsonObj[TIME_TICKER_LABEL]

        # clear prev time then decode if JSON defined
        prev_time_ticker = 0
        if prevJsonObj != None:
            prev_time_ticker = prevJsonObj[TIME_TICKER_LABEL]
            # if different phones, mark as correctly most recent to oldest order
            if jsonObj[PHONE_MOBILE_ID] != prevJsonObj[PHONE_MOBILE_ID]:
                print("isTimeOrdered finds TX ", jsonObj[TX_NAME_LABEL], " swapped from ", prevJsonObj[PHONE_MOBILE_ID], " to ",
                      jsonObj[PHONE_MOBILE_ID])
                return True, time_ticker

        # if time descending, correctly most recent to oldest order
        if time_ticker < prev_time_ticker:
            return True, time_ticker
        else:
            # if first pass, mark as correct & assign time
            if prev_time_ticker == 0:
                return True, time_ticker
            else:
                # invalid time order
                return False, time_ticker

    except isTimeOrdered as e:
        print("isTimeOrder Exception for: ", time_ticker)
        return False, 0
###############################################################################
# tally state transition durations
# def isDuration(snap):
#     # state transition durations should tally to the interval max plus/minus fudge
#     tally =
#     return False
###############################################################################