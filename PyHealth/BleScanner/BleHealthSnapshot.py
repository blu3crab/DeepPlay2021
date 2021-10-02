###############################################################################
#   BleHealthSnapshot
#       class - BLE health metrics for a single TX for a single interval
#
#   BLE health metrics
#       class BleHealthSnapshot:
#
#       # initializer
#       def __init__(self, jsonData):
#       def isIntervalValid(self): return True/False
#       def isKeepAliveCountValid(self): return True/False
#       def toString(self): print("===BleHealth===")
#       def toStateString(self): print("===BleHealth ", self.aTxName, "===")
#
#   Created by MatthewTucker on 24JAN19.
###############################################################################
import json

from datetime import datetime, timezone, timedelta
import pytz

TX_NAME_LABEL = 'aTxName'
KEEP_ALIVE_TICKER_LABEL = 'keepAliveTimeTicker'
TIME_TICKER_LABEL = 'startTime'
PHONE_MOBILE_ID = 'mobileId'

###############################################################################
# BLE health metrics
###############################################################################
class BleHealthSnapshot:

    # connection state enumeration
    CONNECTION_STATE = ['DISCONNECTED', 'SEARCHING', 'CONNECTING', 'NEGOTIATING', 'TRANSPORT_CONNECTED', 'CONNECTED']

    CONNECTION_MAP_ASC = [0, 1, 2, 3, 4, 5]  # ascending state map
    CONNECTION_MAP_DESC = [5, 4, 3, 2, 1, 0]  # descending state map

    DURATION_IDEAL_MS = 900000  # ideal interval duration
    DURATION_FUDGE_MS = 240000   # test fudge factor around ideal

    INTERVAL_IDEAL_PER_DAY = 96  # ideal # intervals per day

    KEEPALIVE_IDEAL_COUNT = 15  # keep alive ideal message count
    KEEPALIVE_FUDGE_COUNT = 3   # keep alive fudge count around ideal


    # initializer
    def __init__(self, jsonData):

        self.currentStateIndex = jsonData['currentStateIndex']
        self.currentStateEnum = jsonData['currentStateEnum']

        self.mobileId = jsonData['mobileId']
        # set phone type indicator based on MobileId pattern
        self.isAndroid = True
        if "-" in self.mobileId:
            self.isAndroid = False

        self.aTxName = jsonData['aTxName']
        self.txSerialNo = jsonData['txSerialNo']

        self.startTime = int(jsonData['startTime'])
        # print("json->", jsonData['startTime'], ", startTime ", self.startTime)
        self.stateTimeTicker = int(jsonData['stateTimeTicker'])
        self.keepAliveTimeTicker = int(jsonData['keepAliveTimeTicker'])

        self.stateChangeCount = list(map(int, jsonData['stateChangeCount']))
        self.minDuration = list(map(int, jsonData['minDuration']))
        self.aveDuration = list(map(int, jsonData['aveDuration']))
        self.maxDuration = list(map(int, jsonData['maxDuration']))

        self.keepAliveCount = int(jsonData['keepAliveCount'])
        self.minKeepAlive = int(jsonData['minKeepAlive'])
        self.aveKeepAlive = int(jsonData['aveKeepAlive'])
        self.maxKeepAlive = int(jsonData['maxKeepAlive'])

    def isIntervalValid(self):
        interval = self.stateTimeTicker - self.startTime
        # if interval greater or less than expected (using fudge factor), return false
        if interval > (self.DURATION_IDEAL_MS + self.DURATION_FUDGE_MS) or interval < (self.DURATION_IDEAL_MS - self.DURATION_FUDGE_MS):
            # print("duration NOT ideal ->", interval, ", ", self.stateTimeTicker, ", ", self.startTime, ", max/fudge=", self.DURATION_IDEAL_MS, ", ", self.DURATION_FUDGE_MS)
            return False
        # interval valid
        return True

    def isKeepAliveCountValid(self):
        keepalive_count = self.keepAliveCount
        # if keep alive count is greater or less than expected (using fudge factor), return false
        if keepalive_count > (self.KEEPALIVE_IDEAL_COUNT + self.KEEPALIVE_FUDGE_COUNT) or keepalive_count < (self.KEEPALIVE_IDEAL_COUNT - self.KEEPALIVE_FUDGE_COUNT):
            # print("keepalive_count NOT ideal ->", keepalive_count, ", ideal/fudge=", self.KEEPALIVE_IDEAL_COUNT, ", ", self.KEEPALIVE_FUDGE_COUNT)
            return False
        # interval valid
        return True

    def toString(self):
        print("===BleHealth===")
        print(self.currentStateIndex)
        print(self.currentStateEnum)
        print(self.mobileId)
        print(self.aTxName)
        print(self.txSerialNo)
        date = datetime.fromtimestamp(self.startTime / 1000.0)
        print(date)
        print(self.startTime)
        print(self.stateTimeTicker)
        print(self.stateChangeCount)
        print(self.minDuration)
        print(self.aveDuration)
        print(self.maxDuration)
        print(self.keepAliveTimeTicker)
        print(self.minKeepAlive)
        print(self.aveKeepAlive)
        print(self.maxKeepAlive)

    def toStateString(self):
        print("===BleHealth ", self.aTxName, "===")
        print(self.currentStateEnum)
        print(self.aTxName, ", ", self.txSerialNo)
        date = datetime.fromtimestamp((self.startTime / 1000.0), tz=pytz.utc)
        print(date, "UTC")
        date = datetime.fromtimestamp(self.startTime / 1000.0)
        print(date, "EST")
        interval = (self.stateTimeTicker - self.startTime)/1000
        print("current time ", self.stateTimeTicker, ", start time ", self.startTime, ", duration ", interval, " secs")
        print("index...state...change count...max secs...ave secs...min secs")
        for state_index in BleHealthSnapshot.CONNECTION_MAP_DESC:
            print(state_index, "-",
                  BleHealthSnapshot.CONNECTION_STATE[state_index], "-",
                  self.stateChangeCount[state_index], "-",
                  self.maxDuration[state_index]/1000, "-",
                  self.aveDuration[state_index]/1000, "-",
                  self.minDuration[state_index]/1000, "-")


###############################################################################
