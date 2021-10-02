###############################################################################
#   BleHealthScanner.ModelTxHealth
#
#   model TX health
#       def modelTxHealth(bleHealthSnapshotCollection, start_time, end_time):
#           return title, percent_duration, discontinuity_tally
#   set title
#       def setTitle(bleHealthSnapshotCollection):
#   set labels
#       def setLabels(discontinuity_tally):
#           return slices_label
#   model discontinuity
#       return duration of significant gap between snapshots & discontinuity indicator
#       def modelDiscontinuity(previous_start_time, current_end_time):
#           return 0, False
#   model by alerting if average keep alive intervals fast, slow or missing
#       return code, duration
#       def modelKeepAlive(bleHealth, currentLineCount):
#           return alertCode, duration
#
#   Created by MatthewTucker on 16MAY19.
###############################################################################

from datetime import datetime, timezone, timedelta
import pytz

import PlotUtils as plotUtils
import Settings

###############################################################################
TAG = 'modelTxHealth'
###############################################################################
# model TX health
def modelTxHealth(bleHealthSnapshotCollection, start_time, end_time):

    # clear alert duration tally for each alert level
    # ALERT_LEVEL_ENUM = ['GREEN', 'YELLOW', 'RED', 'GRAY']
    alert_duration = [0, 0, 0, 0]
    percent_duration = [0, 0, 0, 0]
    # alert discontinuity counter
    discontinuity_tally = 0

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
            if Settings.DEBUG: print(TAG, " GRAY duration ", alert_duration[Settings.ALERT_INDEX_GRAY],
                           " with discontinuity counter ", discontinuity_tally)

        # model by alerting if disconnect duration exceeds threshold
        alertCode, duration = modelKeepAlive(bleHealth, currentLineCount)

        # tally duration for alert code
        alert_duration[alertCode] += duration
        if Settings.DEBUG: print(TAG, " ", Settings.ALERT_COLOR_ENUM[alertCode], " duration updated to ", alert_duration[alertCode])

        # retain current interval end time (bleHealth.stateTimeTicker)
        prev_snapshot_start_time = bleHealth.startTime

    total_duration = 0
    # output total durations
    for alertCode in range(4):
        if Settings.DEBUG: print(TAG, " ", Settings.ALERT_COLOR_ENUM[alertCode], " duration ", alert_duration[alertCode], " ms")
        total_duration += alert_duration[alertCode]
    if Settings.DEBUG: print(TAG, " total duration ", str(total_duration), " ms (", str(total_duration/1000/60/60), " hrs)")
    # out total percentages
    for alertCode in range(4):
        percent_duration[alertCode] = (alert_duration[alertCode]/total_duration) * 100
        if Settings.DEBUG: print(TAG, " ", Settings.ALERT_COLOR_ENUM[alertCode], " percent duration %.2f" % percent_duration[alertCode], " %")

    if Settings.DEBUG: print(TAG, " total (GRAY) discontinuity counter ", discontinuity_tally)

    # # plot pie chart
    # plotUtils.plotPie(title, percent_duration, discontinuity_tally)
    # # plot stacked bar chart
    # plotUtils.plotStackedBar(title, percent_duration, discontinuity_tally)

    return title, percent_duration, discontinuity_tally

###############################################################################
# set title
def setTitle(bleHealthSnapshotCollection):
    # capture display fields
    txName = bleHealthSnapshotCollection[0].aTxName
    startDate = datetime.fromtimestamp((bleHealthSnapshotCollection[0].startTime / 1000.0), tz=pytz.utc)
    endDate = datetime.fromtimestamp((bleHealthSnapshotCollection[len(bleHealthSnapshotCollection)-1].stateTimeTicker / 1000.0), tz=pytz.utc)
    timeLabel = startDate.ctime() + " to " + endDate.ctime()
    title = 'Eversense TX Health for TX ' + txName + '\n' + timeLabel
    return title

###############################################################################
# set labels
def setLabels(discontinuity_tally):
    inactive_label = 'inactive(' + str(discontinuity_tally) + ')'
    slices_label = ['ideal', 'erratic', 'infrequent', inactive_label]
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
# model by alerting if average keep alive intervals fast, slow or missing
#   return code, duration
def modelKeepAlive(bleHealth, currentLineCount):
    # IDEAL_KEEPALIVE_INTERVAL = 60000
    # YELLOW_KEEPALIVE_INTERVAL = 10000
    # RED_KEEPALIVE_INTERVAL = 180000

    alertCode = Settings.ALERT_INDEX_GREEN
    # if not connected, gray alert code
    if bleHealth.currentStateEnum != 'CONNECTED':
        alertCode = Settings.ALERT_INDEX_GRAY
        if Settings.DEBUG:
            print(" Alert code ", Settings.ALERT_COLOR_GRAY, " not connected at interval # ",
                  currentLineCount, "...")
    # if very few or no keep alive, red alert code
    elif (bleHealth.aveKeepAlive == 0 or bleHealth.aveKeepAlive > Settings.RED_KEEPALIVE_INTERVAL):
        alertCode = Settings.ALERT_INDEX_RED
        if Settings.DEBUG:
            # bleHealth.toStateString()
            print(" Alert code ", Settings.ALERT_COLOR_RED, " average keep alive ", bleHealth.aveKeepAlive," at interval # ",
                  currentLineCount, "...")
    # if out of target range, yellow alert code
    elif (bleHealth.aveKeepAlive > (Settings.IDEAL_KEEPALIVE_INTERVAL + Settings.YELLOW_KEEPALIVE_INTERVAL) or
        bleHealth.aveKeepAlive < (Settings.IDEAL_KEEPALIVE_INTERVAL - Settings.YELLOW_KEEPALIVE_INTERVAL)):
        alertCode = Settings.ALERT_INDEX_YELLOW
        if Settings.DEBUG:
            # bleHealth.toStateString()
            print("Alert code ", Settings.ALERT_COLOR_YELLOW, " average keep alive ", bleHealth.aveKeepAlive, " at interval # ",
                  currentLineCount, "...")
    # set duration for current interval
    duration = bleHealth.stateTimeTicker - bleHealth.startTime

    if Settings.DEBUG:
        print("modelDisconnect alert code ", Settings.ALERT_COLOR_ENUM[alertCode], " with interval duration ", str(duration), "...")

    return alertCode, duration

###############################################################################
