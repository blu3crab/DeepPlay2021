###############################################################################
#   BleScanner
#
#       BleScanner op TX-id record-count start-day duration-days
#           op
#               COMMAND_LINE_OPTION_OP_TXLIST = "txlist" -- list unique TX in scan range
#               COMMAND_LINE_OPTION_OP_TXMODEL = "txmodel"  -- model health
#
#           TX-id           -- TX name e.g. DEMO4750, default 1st in list
#
#           record-count    -- DB depth to scan
#
#       e.g. BleScanner txmodel T0026653 1200 1 14
#               model TX T0026653 starting 1 day ago for 2 weeks scanning 1200 records into the DB
#
#       access DB
#       scan for all TX in range
#       if TX in set
#           perform op on TX
#
###############################################################################
# import BleHealthSnapshot as bleHealthSnapshot
from datetime import datetime
import math
import pytz
import sys
import traceback

import BleCheck as bleCheck
import DbUtils as dbUtils
import ModelAppHealth as appModel
import ModelBleHealth as bleModel
import ModelTxHealth as txModel
import PlotUtils as plotUtils
import Settings
###############################################################################
# trace levels
DEBUG = False
INFO = False
WARNING = True
ERROR = True
CRITICAL = True
###############################################################################

# constants
WILDCARD = "*"
NADA = "nada"

COMMAND_LINE_OPTION_OP_HELP = "Usage: blescanner operation txname record-count start-day duration-days\nwhere op = txlist | txmodel\nwhere record-count = # DB records to scan, default=1000"

COMMAND_LINE_OPTION_OP_TXLIST = "txlist"
COMMAND_LINE_OPTION_OP_TXMODEL = "txmodel"

COMMAND_LINE_ARG_TXNAME_ALL = "*"
COMMAND_LINE_ARG_RECORDCOUNT_DEFAULT = 1000
COMMAND_LINE_ARG_START_OFFSET_DEFAULT = 0
COMMAND_LINE_ARG_DURATION_DEFAULT = 14
COMMAND_LINE_ARG_DIRPATH_DEFAULT = ""

COMMAND_LINE_ARG_OP = 1
COMMAND_LINE_ARG_TXNAME = 2
COMMAND_LINE_ARG_RECORDCOUNT = 3
COMMAND_LINE_ARG_START_OFFSET = 4
COMMAND_LINE_ARG_DURATION = 5
COMMAND_LINE_ARG_DIRPATH = 6

# flags
PANDA_ENABLED = False           # dump raw panda dataset
BLESNAP_PRINT_ENABLED = True # dump raw bl health snapshots
show_flag = False               # plot

###############################################################################
def main():

    # fetch command line options
    print("BleScanner command line ->")
    print(sys.argv, len(sys.argv))
    print(COMMAND_LINE_OPTION_OP_HELP)

    command_line_op = get_command_line_option(COMMAND_LINE_ARG_OP)
    command_line_txname = get_command_line_option(COMMAND_LINE_ARG_TXNAME)
    command_line_record_count = get_command_line_option(COMMAND_LINE_ARG_RECORDCOUNT)
    command_line_start_offset = get_command_line_option(COMMAND_LINE_ARG_START_OFFSET)
    command_line_duration = get_command_line_option(COMMAND_LINE_ARG_DURATION)
    command_line_dirpath = get_command_line_option(COMMAND_LINE_ARG_DIRPATH)

    # command_line_op = 'txlist'
    try:
        # assign target DB
        # target_db = Settings.OUS_STAGING
        target_db = Settings.US_STAGING
        # target_db = Settings.US_PRODUCTION_COPY
        db_connection = dbUtils.openDb(target_db)
        if db_connection == 0:
            print("BleScanner - unable to access DB server ", target_db)
            return

        # scan for unique TX
        tx_all_list, empty_row_count = dbUtils.getBleTx(db_connection, command_line_record_count)
        if Settings.INFO:
            print("BleScanner TX list count: ", len(tx_all_list))
            print("BleScanner TX list: ", tx_all_list)
            print("BleScanner empty row count: ", empty_row_count)

        if command_line_op == COMMAND_LINE_OPTION_OP_TXLIST:
            return

        # set target TX list
        tx_target_list = []
        if command_line_txname == COMMAND_LINE_ARG_TXNAME_ALL:
            tx_target_list = tx_all_list
        else:
            tx_target_list.append(command_line_txname)
        # command line option overrides
        # command_line_op = "txmodel"
        # command_line_txname = "T0026653"
        # command_line_record_count = 4800
        # command_line_start_offset = 0
        command_line_duration = 1
        if Settings.WARNING: print("BleScanner op: ", command_line_op, ", TX name: ", command_line_txname, ", record count: ",
              str(command_line_record_count),
              ", start offset (days ago): ", str(command_line_start_offset), ", duration(days): ",
              str(command_line_duration))
        # tx_target_list.append("DEMO4750")
        # tx_target_list.append("DEMO4906")
        # tx_target_list.append("DEMO1420")
        # tx_target_list.append("T0048094")
        # tx_target_list.append("DEMO3851")
        tx_target_list = []
        tx_target_list.append("T0026949")
        # tx_target_list.append("T0082902")
        # tx_target_list.append("T0026653")
        # tx_target_list.append("DEMO2127")
        # tx_target_list.append("DEMO4119")
        # tx_target_list.append("T0026654")
        # tx_target_list.append("DEMO1049")
        if Settings.INFO: print("BleScanner target list: ", tx_target_list)

        start_time, end_time = bleCheck.getTimeFromOffsets(int(command_line_start_offset), int(command_line_duration))

        # for each TX in target list
        tx_target_found = False
        for tx in tx_target_list:
            # if Tx target in all TX list
            if tx in tx_all_list:
                tx_target_found = True
                # generate datasets - default start record
                ble_snaps, df_collection, valid_row_count, empty_row_count, row_out_of_order, initial_interval_gap, interval_gap_count = \
                    dbUtils.getBleTxDataset(db_connection, 0, command_line_record_count, tx, start_time, end_time, PANDA_ENABLED)
                if len(ble_snaps) > 0:
                    if ble_snaps[0].isAndroid:
                        if Settings.INFO: print("\n========= TX ", tx, " (Android) ==========")
                        # plot = False
                        plot = True
                    else:
                        if Settings.INFO: print("\n========= TX ", tx, " (iOS) ==========")
                        plot = True
                else:
                    print("\nBleScanner BLE snapshots empty...exiting...")
                    return

                if Settings.INFO:
                    print("\nBleScanner row counts-> valid: " + str(valid_row_count) + ", empty: " + str(empty_row_count) + ", out of order: " + str(row_out_of_order))
                    print("BleScanner initial interval gap: " + str(math.trunc(initial_interval_gap)) + ", interval gap count: " + str(interval_gap_count) + "\n")
                    print("BleScanner using : " + str(valid_row_count-row_out_of_order) + " rows after out-of-order removed." + "\n")
                # if enabled, dump raw data
                if PANDA_ENABLED:
                    print(df_collection.to_string())
                if BLESNAP_PRINT_ENABLED:
                    for snap in ble_snaps:
                        # print(snap.aTxName, ", ", snap.startTime, ", ", snap.stateChangeCount, ", ", snap.currentStateEnum)
                        # print(snap)
                        print(snap.toStateString())

                if command_line_op == COMMAND_LINE_OPTION_OP_TXMODEL:
                    # model BLE health
                    title, ble_percent_duration, discontinuity_tally, disconnect_tally_red, disconnect_tally_yellow = \
                        bleModel.modelBleHealth(ble_snaps, start_time, end_time)
                    # set labels e.g. ['ideal', 'degraded', 'unavailable', inactive_label]
                    ble_slices_label = bleModel.setLabels(discontinuity_tally, disconnect_tally_red, disconnect_tally_yellow)
                    if plot and len(tx_target_list) == 1:
                        # plot pie chart
                        filepath = getFilePath(command_line_dirpath, tx)
                        plotUtils.plotPie(filepath, title, ble_percent_duration, discontinuity_tally, ble_slices_label)

                    # model APP health
                    title, app_percent_duration, discontinuity_tally = appModel.modelAppHealth(ble_snaps, start_time, end_time)
                    # set labels e.g. ['ideal', 'delayed', 'degraded', inactive_label]
                    app_slices_label = appModel.setLabels(discontinuity_tally)
                    if plot and len(tx_target_list) == 1:
                        # plot pie chart
                        filepath = getFilePath(command_line_dirpath, tx)
                        plotUtils.plotPie(filepath, title, app_percent_duration, discontinuity_tally, app_slices_label)

                    # model BLE health
                    title, tx_percent_duration, discontinuity_tally = txModel.modelTxHealth(ble_snaps, start_time, end_time)
                    # set labels e.g. ['ideal', 'degraded', 'unavailable', inactive_label]
                    tx_slices_label = txModel.setLabels(discontinuity_tally)
                    if plot and len(tx_target_list) == 1:
                        # plot pie chart
                        filepath = getFilePath(command_line_dirpath, tx)
                        plotUtils.plotPie(filepath, title, tx_percent_duration, discontinuity_tally, tx_slices_label)

                    if plot:
                        # set title for plots
                        title = getTitle(ble_snaps)
                        # plot multi-model stacked bar chart
                        filepath = getFilePath(command_line_dirpath, tx)
                        plotUtils.plotStackedBar(filepath, title, ble_percent_duration, app_percent_duration, tx_percent_duration, discontinuity_tally, ble_slices_label)

        if not tx_target_found:
            if Settings.ERROR: print("BleScanner Target TX ", tx_target_list, " not found in ", tx_all_list)
    except Exception as e:
        traceback.print_exc()
        if Settings.CRITICAL: print("BleScanner Exception raised...exiting...")

        if Settings.INFO: print("BleScanner abbiamo finito...")


###############################################################################
def getFilePath(command_line_dirpath, tx):
    # datetime.today().strftime('%Y-%m-%d')
    filename = tx + "-" + datetime.today().strftime('%Y-%m-%d-%H-%M-%S') + ".png"
    # print("BleScanner filename ", filename)
    # command_line_dirpath = "C:\Tuc\Image2019\BleHealth"
    # if not empty
    if command_line_dirpath: filepath = command_line_dirpath + "\\" + filename
    if Settings.INFO: print("BleScanner pathname ", filepath)
    return filepath

###############################################################################
# set title
def getTitle(bleHealthSnapshotCollection):
    # capture display fields
    txName = bleHealthSnapshotCollection[0].aTxName
    startDate = datetime.fromtimestamp((bleHealthSnapshotCollection[0].startTime / 1000.0), tz=pytz.utc)
    endDate = datetime.fromtimestamp((bleHealthSnapshotCollection[len(bleHealthSnapshotCollection)-1].stateTimeTicker / 1000.0), tz=pytz.utc)
    timeLabel = startDate.ctime() + " to " + endDate.ctime()
    osType = "Android"
    if not bleHealthSnapshotCollection[0].isAndroid: osType = "iOS"
    title = 'Eversense (' + osType + ') Health for TX ' + txName + '\n' + timeLabel
    return title
###############################################################################
def get_command_line_option(arg):
    if len(sys.argv) > arg:
        option = sys.argv[arg]
    else:
        option = NADA

    if arg == COMMAND_LINE_ARG_OP:
        if option == COMMAND_LINE_OPTION_OP_TXLIST or \
           option == COMMAND_LINE_OPTION_OP_TXMODEL:
            return option
        else:
            return COMMAND_LINE_OPTION_OP_TXLIST

    if arg == COMMAND_LINE_ARG_TXNAME:
        if option == NADA:
            return COMMAND_LINE_ARG_TXNAME_ALL
        else:
            return option

    if arg == COMMAND_LINE_ARG_RECORDCOUNT:
        if option == NADA:
            return COMMAND_LINE_ARG_RECORDCOUNT_DEFAULT
        else:
            return option

    if arg == COMMAND_LINE_ARG_START_OFFSET:
        if option == NADA:
            return COMMAND_LINE_ARG_START_OFFSET_DEFAULT
        else:
            return option

    if arg == COMMAND_LINE_ARG_DURATION:
        if option == NADA:
            return COMMAND_LINE_ARG_DURATION_DEFAULT
        else:
            return option

    if arg == COMMAND_LINE_ARG_DIRPATH:
        if option == NADA:
            return COMMAND_LINE_ARG_DIRPATH_DEFAULT
        else:
            return option

    return NADA

###############################################################################
# launch main
if __name__ == "__main__":
    main()
###############################################################################
