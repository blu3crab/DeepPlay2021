###############################################################################
#   BleHealthScanner.ModelBleHealth
#
#       model BLE health
#           def modelBleHealth(bleHealthSnapshotCollection, start_time, end_time):
#               return title, percent_duration, discontinuity_tally
#       set title
#           def setTitle(bleHealthSnapshotCollection):
#               return title
#       set title
#           def setLabels(discontinuity_tally):
#               return slices_label
#       model discontinuity
#           return duration of significant gap between snapshots & discontinuity indicator
#           def modelDiscontinuity(previous_start_time, current_end_time):
#               return 0, False
#       model by alerting if disconnect duration exceeds threshold
#           return code, duration
#       def modelDisconnect(bleHealth, currentLineCount):
#           return alertCode, duration
#
#   Created by MatthewTucker on 16MAY19.
###############################################################################

from datetime import datetime, timezone, timedelta
import pytz

import PlotUtils as plotUtils
import Settings

###############################################################################
# model BLE health
def modelBleHealth(bleHealthSnapshotCollection, start_time, end_time):

    # clear alert duration tally for each alert level
    # ALERT_LEVEL_ENUM = ['GREEN', 'YELLOW', 'RED', 'GRAY']
    alert_duration = [0, 0, 0, 0]
    percent_duration = [0, 0, 0, 0]
    # alert discontinuity counter
    discontinuity_tally = 0
    disconnect_tally_red = 0
    disconnect_tally_yellow = 0

    currentLineCount = 0
    # firstLine = True
    prev_snapshot_start_time = 0

    # set title
    title = setTitle(bleHealthSnapshotCollection)
    # for each snapshot in collection
    for bleHealth in bleHealthSnapshotCollection:
        currentLineCount += 1
        # if not first pass, model discontinuity
        if prev_snapshot_start_time != 0:
            duration, discontinuity = modelDiscontinuity(prev_snapshot_start_time, bleHealth.stateTimeTicker)
            # if previous snapshot start not close to this interval end
            if duration > 0:
                # model as GREY (missing)
                alert_duration[Settings.ALERT_INDEX_GRAY] += duration
            if discontinuity:
                # bump discontinuity counter
                discontinuity_tally += 1
            if Settings.DEBUG: print("modelBleHealth GRAY duration ", alert_duration[Settings.ALERT_INDEX_GRAY],
                           " with discontinuity counter ", discontinuity_tally)

        # model by alerting if disconnect duration exceeds threshold
        alertCode, duration = modelDisconnect(bleHealth, currentLineCount)

        # if no alerts, model state change
        if alertCode == Settings.ALERT_INDEX_GREEN:
            # model by alerting if state change exceeds threshold
            alertCode, duration = modelStateChange(bleHealth, currentLineCount)

        # if red or yellow alert level, tally state change count for CONNECTED
        if alertCode == Settings.ALERT_INDEX_RED:
            disconnect_tally_red += bleHealth.stateChangeCount[5]
        elif alertCode == Settings.ALERT_INDEX_YELLOW:
            disconnect_tally_yellow += bleHealth.stateChangeCount[5]

        # tally duration for alert code
        alert_duration[alertCode] += duration
        if Settings.DEBUG: print("modelBleHealth ", Settings.ALERT_COLOR_ENUM[alertCode], " duration updated to ", alert_duration[alertCode])

        # retain current interval end time (bleHealth.stateTimeTicker)
        prev_snapshot_start_time = bleHealth.startTime

    total_duration = 0
    # output total durations
    for alertCode in range(4):
        if Settings.DEBUG: print("modelBleHealth ", Settings.ALERT_COLOR_ENUM[alertCode], " duration ", alert_duration[alertCode], " ms")
        total_duration += alert_duration[alertCode]
    if Settings.DEBUG: print("modelBleHealth total duration ", str(total_duration), " ms (", str(total_duration/1000/60/60), " hrs)")

    # if duration non-zero
    if total_duration > 0:
        # format percentages from durations
        for alertCode in range(4):
            percent_duration[alertCode] = (alert_duration[alertCode]/total_duration) * 100
            if Settings.DEBUG: print("modelBleHealth ", Settings.ALERT_COLOR_ENUM[alertCode], " percent duration %.2f" % percent_duration[alertCode], " %")

    if Settings.DEBUG: print("modelBleHealth total (GRAY) discontinuity counter ", discontinuity_tally)

    # # plot pie chart
    # plotUtils.plotPie(title, percent_duration, discontinuity_tally)
    # # plot stacked bar chart
    # plotUtils.plotStackedBar(title, percent_duration, discontinuity_tally)

    return title, percent_duration, discontinuity_tally, disconnect_tally_red, disconnect_tally_yellow

###############################################################################
# set title
def setTitle(bleHealthSnapshotCollection):
    # capture display fields
    txName = bleHealthSnapshotCollection[0].aTxName
    startDate = datetime.fromtimestamp((bleHealthSnapshotCollection[0].startTime / 1000.0), tz=pytz.utc)
    endDate = datetime.fromtimestamp((bleHealthSnapshotCollection[len(bleHealthSnapshotCollection)-1].stateTimeTicker / 1000.0), tz=pytz.utc)
    timeLabel = startDate.ctime() + " to " + endDate.ctime()
    title = 'Eversense BLE Health for TX ' + txName + '\n' + timeLabel
    return title
###############################################################################
# set title
def setLabels(discontinuity_tally, disconnect_tally_red, disconnect_tally_yellow):
    inactive_label = 'inactive(' + str(discontinuity_tally) + ')'
    unavailable_label = 'unavailable(' + str(disconnect_tally_red) + ')'
    degraded_label = 'degraded(' + str(disconnect_tally_yellow) + ')'
    slices_label = ['ideal', degraded_label, unavailable_label, inactive_label]
    return slices_label

###############################################################################
# model discontinuity
#   return duration of significant gap between snapshots & discontinuity indicator
def modelDiscontinuity(previous_start_time, current_end_time):
    # set duration between last snapshot start & this snapshot end
    duration = previous_start_time - current_end_time
    # previous snapshot start not close to this interval end
    if duration > Settings.DISCONTINUITY_DURATION_FUDGE or duration < -Settings.DISCONTINUITY_DURATION_FUDGE:
        # return duration of significant gap between snapshots & discontinuity indicator
        return duration, True
    # timing gap is small, no discontinuity, reset to 0
    return 0, False

###############################################################################
# model by alerting if disconnect duration exceeds threshold
#   return code, duration
def modelDisconnect(bleHealth, currentLineCount):
    alertCode = Settings.ALERT_INDEX_GREEN

    # tally the max duration of all disconnected states
    max_duration_tally = 0
    for state_index in bleHealth.CONNECTION_MAP_DESC:
        if Settings.DEBUG: print(state_index, "-", bleHealth.CONNECTION_STATE[state_index])
        if not (bleHealth.CONNECTION_STATE[state_index] == 'CONNECTED'):
            max_duration_tally += bleHealth.maxDuration[state_index]

    # set alert code based on disconnected duration tally
    if max_duration_tally / 1000 > Settings.RED_HIGH_WATER_MARK_DISCONNECT_DURATION * 60:
        alertCode = Settings.ALERT_INDEX_RED
        if Settings.DEBUG:
            # bleHealth.toStateString()
            print(" Alert code ", Settings.ALERT_COLOR_RED, " disconnect duration exceeded at interval # ",
                  currentLineCount, "...")
    elif max_duration_tally / 1000 > Settings.YELLOW_HIGH_WATER_MARK_DISCONNECT_DURATION * 60:
        alertCode = Settings.ALERT_INDEX_YELLOW
        if Settings.DEBUG:
            # bleHealth.toStateString()
            print("Alert code ", Settings.ALERT_COLOR_YELLOW, " disconnect duration exceeded at interval # ",
                  currentLineCount, "...")
    # set duration for current interval
    duration = bleHealth.stateTimeTicker - bleHealth.startTime
    if Settings.DEBUG:
        print("modelDisconnect alert code ", Settings.ALERT_COLOR_ENUM[alertCode], " with interval duration ", str(duration), "...")

    return alertCode, duration

###############################################################################
# model by alerting if disconnect duration exceeds threshold
#   return code, duration
def modelStateChange(bleHealth, currentLineCount):
    alertCode = Settings.ALERT_INDEX_GREEN

    # tally & alert if N state changes in interval
    state_change_count = 0
    for state_index in bleHealth.CONNECTION_MAP_DESC:
        if Settings.DEBUG: print(state_index, "-", bleHealth.CONNECTION_STATE[state_index])
        state_change_count += bleHealth.stateChangeCount[state_index]

    # set alert code based on stae change count
    if state_change_count > Settings.RED_HIGH_WATER_MARK_STATE_CHANGE:
        alertCode = Settings.ALERT_INDEX_RED
        if Settings.DEBUG:
            # bleHealth.toStateString()
            print("Alert code ", Settings.ALERT_COLOR_ENUM[alertCode], " connection state change count at interval # ",
                  currentLineCount, "...")
    elif state_change_count > Settings.YELLOW_HIGH_WATER_MARK_STATE_CHANGE:
        alertCode = Settings.ALERT_INDEX_YELLOW
        if Settings.DEBUG:
            # bleHealth.toStateString()
            print("Alert code ", Settings.ALERT_COLOR_ENUM[alertCode], " connection state change count at interval # ",
                  currentLineCount, "...")
    # set duration for current interval
    duration = bleHealth.stateTimeTicker - bleHealth.startTime
    if Settings.DEBUG:
        print("modelStateChange alert code ", Settings.ALERT_COLOR_ENUM[alertCode], " with interval duration ", str(duration), "...")

    return alertCode, duration

###############################################################################
