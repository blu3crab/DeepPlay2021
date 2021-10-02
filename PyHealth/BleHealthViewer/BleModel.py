###############################################################################
#   BleHealthViewer.BleModel
#
#
#   Created by MatthewTucker on 16MAY19.
###############################################################################
import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta
import pytz

import BleHealthSnapshot as bleHealthSnapshot
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
# model individual TX
def modelAlerts(bleHealthSnapshotCollection, show_flag):

    alertCountTimerInterval = 0;
    alertCountDisconnectDuration = 0;
    alertCountStateChange = 0;

    stateGraph = []
    anyGraph = []

    currentLineCount = 0
    scanLineCount = 0
    firstLine = True
    txFound = False

    # for each line
    for bleHealth in bleHealthSnapshotCollection:
        currentLineCount += 1
        txName = bleHealth.aTxName

        txFound = True;
        if firstLine:
            startDate = datetime.fromtimestamp((bleHealth.startTime / 1000.0), tz=pytz.utc)
            endDate = datetime.fromtimestamp((bleHealth.stateTimeTicker / 1000.0), tz=pytz.utc)
            firstLine = False
        else:
            endDate = datetime.fromtimestamp((bleHealth.stateTimeTicker / 1000.0), tz=pytz.utc)

        # bump count of scanned lines of interest
        scanLineCount += 1
        # tally & alert if disconnect duration exceeds threshold
        max_duration_tally = 0
        for state_index in bleHealth.CONNECTION_MAP_DESC:
            #            print(state_index, "-", BleHealth.CONNECTION_STATE[state_index])
            if not (bleHealth.CONNECTION_STATE[state_index] == 'CONNECTED'):
                max_duration_tally += bleHealth.maxDuration[state_index]

        if max_duration_tally / 1000 > RED_HIGH_WATER_MARK_DISCONNECT_DURATION * 60:
            alertCountDisconnectDuration += 1
            alertCode = setAlertCode('RED')
            if show_flag: bleHealth.toStateString()
            print(" Alert code ", ALERT_LEVEL_ENUM[alertCode], " disconnect duration exceeded at interval # ",
                  currentLineCount, "...")
        elif max_duration_tally / 1000 > YELLOW_HIGH_WATER_MARK_DISCONNECT_DURATION * 60:
            alertCountDisconnectDuration += 1
            alertCode = setAlertCode('YELLOW')
            if show_flag: bleHealth.toStateString()
            print("Alert code ", ALERT_LEVEL_ENUM[alertCode], " disconnect duration exceeded at interval # ",
                  currentLineCount, "...")

        # tally & alert if N state changes in interval
        state_change_count = 0
        for state_index in bleHealth.CONNECTION_MAP_DESC:
            #            print(state_index, "-", BleHealth.CONNECTION_STATE[state_index])
            state_change_count += bleHealth.stateChangeCount[state_index]
        if state_change_count > RED_HIGH_WATER_MARK_STATE_CHANGE:
            alertCountStateChange += 1
            alertCode = setAlertCode('RED')
            if show_flag: bleHealth.toStateString()
            print("Alert code ", ALERT_LEVEL_ENUM[alertCode], " connection state change count at interval # ",
                  currentLineCount, "...")
        elif state_change_count > YELLOW_HIGH_WATER_MARK_STATE_CHANGE:
            alertCountStateChange += 1
            alertCode = setAlertCode('YELLOW')
            if show_flag: bleHealth.toStateString()
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
            # alertCode = setAlertCode('BLACK')
            # timerInterval = (bleHealth.stateTimeTicker - bleHealth.startTime)/1000
            # # bleHealth.toString()
            # print("Alert code ", ALERT_LEVEL_ENUM[alertCode], " timer invalid ", timerInterval, " secs at interval # ", currentLineCount, "...")

    print("\nBleHealth scan ", scanLineCount, " intervals complete for TX name ", txName)
    print("\nBleHealth scan with ", alertCountTimerInterval, " of ", currentLineCount, " timer interval alerts...")
    print("\nBleHealth scan with ", alertCountDisconnectDuration, " disconnect time alerts...")
    print("\nBleHealth scan with ", alertCountStateChange, " state change alerts...")

    # if txFound and show_flag:
    #     plotAlerts(txName, startDate, endDate, stateGraph, anyGraph)

    return txName, startDate, endDate, stateGraph, anyGraph
    print("\nmodelAlerts -> arrivederci, baby!")

def plotAlerts(txName, startDate, endDate, stateGraph, anyGraph):

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
###############################################################################
def setAlertCode(color):
    return ALERT_LEVEL_ENUM.index(color)

###############################################################################
