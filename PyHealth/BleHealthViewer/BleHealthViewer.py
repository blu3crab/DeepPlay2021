###############################################################################
#   BleHealthViewer
#       access DB
#       scan for all TX in range
#       show TX reporting
#       show TX silent
#
#   Created by MatthewTucker on 24JAN19.
###############################################################################
import csv
import os
import sys

import pymssql as pymssql
import xlrd

import json

import unicodedata

# Helper libraries
import numpy as np
import matplotlib.pyplot as plt

import json
from pprint import pprint
import io as io
from datetime import datetime, timezone, timedelta
import pytz

try:
    conn = pymssql.connect(
        database="DB_EversenseDMS_3.0",
        user="sens04dbstaging",
        server="46.17.89.55",
        password="uqf!+4yD!x8U%jCx"
    )
    print("db connection is GOOD!")

except:
    print("unable to connect to the database")


NADA = "nada"
COMMAND_LINE_OPTIONS = "TARGET_DIR TX_NAME START_TIME DURATION"
COMMAND_LINE_ARG_TARGET_DIR = 1
COMMAND_LINE_ARG_TX_NAME = 2
COMMAND_LINE_ARG_START_TIME = 3
COMMAND_LINE_ARG_DURATION = 4

###############################################################################
# json labels
###############################################################################


class BleHealth:
    # # connection state enumeration is unfortunately in random order
    # CONNECTION_STATE = ['CONNECTED', 'DISCONNECTED', 'CONNECTING', 'NEGOTIATING', 'SEARCHING', 'TRANSPORT_CONNECTED']
    #
    # CONNECTION_MAP_ASC = [1, 4, 2, 3, 5, 0]  # ascending state map
    # CONNECTION_MAP_DESC = [0, 5, 3, 2, 4, 1]  # descending state map

    CONNECTION_STATE = ['DISCONNECTED', 'SEARCHING', 'CONNECTING', 'NEGOTIATING', 'TRANSPORT_CONNECTED', 'CONNECTED']

    CONNECTION_MAP_ASC = [0, 1, 2, 3, 4, 5]  # ascending state map
    CONNECTION_MAP_DESC = [5, 4, 3, 2, 1, 0]  # descending state map

    INTERVAL_MAX_MS = 900000
    INTERVAL_FUDGE = 60000

    # initializer
    def __init__(self, jsonData):
        self.currentStateIndex = jsonData['currentStateIndex']
        self.currentStateEnum = jsonData['currentStateEnum']

        self.mobileId = jsonData['mobileId']
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
        if interval > (self.INTERVAL_MAX_MS + self.INTERVAL_FUDGE) or interval < (self.INTERVAL_MAX_MS - self.INTERVAL_FUDGE):
            print("interval=", interval, ", ", self.stateTimeTicker, ", ", self.startTime, ", max/fudge=", self.INTERVAL_MAX_MS, ", ", self.INTERVAL_FUDGE)
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
        for state_index in BleHealth.CONNECTION_MAP_DESC:
            print(state_index, "-",
                  BleHealth.CONNECTION_STATE[state_index], "-",
                  self.stateChangeCount[state_index], "-",
                  self.maxDuration[state_index]/1000, "-",
                  self.aveDuration[state_index]/1000, "-",
                  self.minDuration[state_index]/1000, "-")


###############################################################################
ALERT_LEVEL_ENUM = ['GREEN', 'YELLOW', 'RED', 'BLACK']

# constants
WILDCARD = "*"
# set alert water marks
RED_HIGH_WATER_MARK_DISCONNECT_DURATION = 5
YELLOW_HIGH_WATER_MARK_DISCONNECT_DURATION = 3
RED_HIGH_WATER_MARK_STATE_CHANGE = 8
YELLOW_HIGH_WATER_MARK_STATE_CHANGE = 5

###############################################################################
def main():
    alertCountTimerInterval = 0;
    alertCountDisconnectDuration = 0;
    alertCountStateChange = 0;

    # ensure command line options are coherent
    if not(validate_command_arg()):
        exit()

    # get dir path & target file list
    dir_path, target_list = get_target_dir_path(".json")
    # print(dir_path, "\n", target_list)

    txName = get_txName()

    print("---ascending---")
    for state_index in BleHealth.CONNECTION_MAP_ASC:
        print(state_index, "-", BleHealth.CONNECTION_STATE[state_index])
    print("---descending---")
    for state_index in BleHealth.CONNECTION_MAP_DESC:
        print(state_index, "-", BleHealth.CONNECTION_STATE[state_index])

    for fileInx in range(0, len(target_list)):
        # open target file
    #    f = open("DEMO-4119-4750-1420-weekend-22jan19.json", "r")
        filename = dir_path + "\\" + target_list[fileInx]
        print("opening->", filename)
        f = open(filename, "r")
        # read json lines into list
        linelist = f.readlines()
        totalLineCount = len(linelist)
        print("line count: ", totalLineCount)

        stateGraph = []
        anyGraph = []

        currentLineCount = 0
        scanLineCount = 0
        firstLine = True
        txFound = False
        # for each line
        for line in range(0, totalLineCount):
            currentLineCount += 1
            # print("linelist->", linelist[line])
            # decode json
            data = json.load(io.StringIO(str(linelist[line])))
            # print(currentLineCount, "-",data)
            # convert incoming data fields
            bleHealth = BleHealth(data)

            # if currentLineCount == 1:
            #     startDate = datetime.fromtimestamp((bleHealth.startTime / 1000.0), tz=pytz.utc)
            # else:
            #     endDate = datetime.fromtimestamp((bleHealth.stateTimeTicker / 1000.0), tz=pytz.utc)
            #
            if (bleHealth.aTxName == txName or
                    bleHealth.aTxName == WILDCARD):
                txFound = True;
                if firstLine:
                    startDate = datetime.fromtimestamp((bleHealth.startTime / 1000.0), tz=pytz.utc)
                    firstLine = False
                else:
                    endDate = datetime.fromtimestamp((bleHealth.stateTimeTicker / 1000.0), tz=pytz.utc)

                # bump count of scanned lines of interest
                scanLineCount += 1
                # tally & alert if disconnect duration exceeds threshold
                max_duration_tally = 0
                for state_index in BleHealth.CONNECTION_MAP_DESC:
                    #            print(state_index, "-", BleHealth.CONNECTION_STATE[state_index])
                    if not (BleHealth.CONNECTION_STATE[state_index] == 'CONNECTED'):
                        max_duration_tally += bleHealth.maxDuration[state_index]

                if max_duration_tally / 1000 > RED_HIGH_WATER_MARK_DISCONNECT_DURATION * 60:
                    alertCountDisconnectDuration += 1
                    alertCode = setAlertCode('RED')
                    bleHealth.toStateString()
                    print(" Alert code ", ALERT_LEVEL_ENUM[alertCode], " disconnect duration exceeded at interval # ",
                          currentLineCount, "...")
                elif max_duration_tally / 1000 > YELLOW_HIGH_WATER_MARK_DISCONNECT_DURATION * 60:
                    alertCountDisconnectDuration += 1
                    alertCode = setAlertCode('YELLOW')
                    bleHealth.toStateString()
                    print("Alert code ", ALERT_LEVEL_ENUM[alertCode], " disconnect duration exceeded at interval # ",
                          currentLineCount, "...")

                # tally & alert if N state changes in interval
                state_change_count = 0
                for state_index in BleHealth.CONNECTION_MAP_DESC:
                    #            print(state_index, "-", BleHealth.CONNECTION_STATE[state_index])
                    state_change_count += bleHealth.stateChangeCount[state_index]
                if state_change_count > RED_HIGH_WATER_MARK_STATE_CHANGE:
                    alertCountStateChange += 1
                    alertCode = setAlertCode('RED')
                    bleHealth.toStateString()
                    print("Alert code ", ALERT_LEVEL_ENUM[alertCode], " connection state change count at interval # ",
                          currentLineCount, "...")
                elif state_change_count > YELLOW_HIGH_WATER_MARK_STATE_CHANGE:
                    alertCountStateChange += 1
                    alertCode = setAlertCode('YELLOW')
                    bleHealth.toStateString()
                    print("Alert code ", ALERT_LEVEL_ENUM[alertCode], " connection state change count at interval # ",
                          currentLineCount, "...")

                if max_duration_tally / 1000 > YELLOW_HIGH_WATER_MARK_DISCONNECT_DURATION * 60 or state_change_count > YELLOW_HIGH_WATER_MARK_STATE_CHANGE:
                    stateGraph.append(0)
                else:
                    stateGraph.append(5)
                if max_duration_tally > 0:
                    anyGraph.append(0)
                else:
                    anyGraph.append(5)

                # if interval invalid
                if not(bleHealth.isIntervalValid()):
                    alertCountTimerInterval += 1
                    alertCode = setAlertCode('BLACK')
                    timerInterval = (bleHealth.stateTimeTicker - bleHealth.startTime)/1000
                    # bleHealth.toString()
                    print("Alert code ", ALERT_LEVEL_ENUM[alertCode], " timer invalid ", timerInterval, " secs at interval # ", currentLineCount, "...")

        print("\nBleHealth scan ", scanLineCount, " of ", totalLineCount, " intervals complete for TX name ", txName)
        print("\nBleHealth scan with ", alertCountTimerInterval, " timer interval alerts...")
        print("\nBleHealth scan with ", alertCountDisconnectDuration, " disconnect time alerts...")
        print("\nBleHealth scan with ", alertCountDisconnectDuration, " state change alerts...")

        # # init state graph as list
        #stateGraph = [1] * totalLineCount
        # f = []
        # #
        # for i in range(totalLineCount):
        #     f.append(2)

        # print(stateGraph)
        # print(f)
        # plt.figure()
        # _ = plt.hist(f, bins=np.linspace(0, totalLineCount))
        # plt.title('BLE Health')
        # plt.ylim([0, 6])
        # plt.show()

        # import matplotlib.pyplot as plt
        # import numpy as np
        # %matplotlib inline
        # x = np.random.normal(size=1000)
        # plt.hist(f, bins=totalLineCount)
        # plt.ylabel('BLE Health')

        # stateList = [0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0]
        # plt.hist(stateList, density=1, bins=10)
        # plt.axis([0, 9, 0, 6])
        # # axis([xmin,xmax,ymin,ymax])
        # plt.xlabel('Time')
        # plt.ylabel('State')

        # stateGraph = [0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0]

        if txFound:
            # x_range = range(totalLineCount)
            title = 'BLE Health TX ' + txName
            plt.title(title)
            timeLabel = startDate.ctime() + " to " + endDate.ctime()

            fileLabel = timeLabel
            fileLabel = fileLabel.replace(":", "-")
            fileLabel = fileLabel.replace(" ", "")
            filename = 'BLE Health ' + txName + "-" + fileLabel
            print(filename)

            plt.xlabel(timeLabel)
            plt.ylabel('BLE State')
            x_range = range(len(stateGraph))
            plt.plot(x_range, anyGraph, 'r',
                     x_range, stateGraph, 'g')
    # show all plots
    plt.show()


    print("\narrivederci, baby!")

#########################################
def setAlertCode(color):
    return ALERT_LEVEL_ENUM.index(color)

###############################################################################
def validate_command_arg():
    print("Hola! Command line parameters->")
    print(sys.argv, len(sys.argv))
    if not len(sys.argv) > 4:
        print("Oops!  Errorneous command line, try this, por favor...\n ", COMMAND_LINE_OPTIONS)
        return False
    return True

###############################################################################
# get target dir path from args
#       returns path or NADA
def get_target_dir_path(file_ext):

    # path of executing python file
    # print("\nget_target_dir_path entered->\n")
    full_path = os.path.realpath(__file__)
    # print("realpath->", full_path)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    # print("dirname->", dir_path)

    cwd = os.getcwd()
    # print("getcwd->", cwd)

    dir_path = sys.argv[COMMAND_LINE_ARG_TARGET_DIR]
    # print("dirname->", dir_path)

    target_list = os.listdir(dir_path)
    for file in target_list:
        if file.endswith(file_ext):
            print("target->", file)
        else:
            print("unk->", file)

    print("get_target_dir_path exit->", dir_path)
    return dir_path, target_list

###############################################################################
# get target dir path from args
#       returns path or NADA
def get_txName():
    txName = sys.argv[COMMAND_LINE_ARG_TX_NAME]
    print("txName->", txName)
    return txName
###############################################################################
# launch main
if __name__ == "__main__":
    main()


###############################################################################
