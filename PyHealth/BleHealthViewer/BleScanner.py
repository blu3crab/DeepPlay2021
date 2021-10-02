###############################################################################
#   BleScanner
#
#       BleScanner op TX-id record-count
#           op = TxList     -- list unique TX in scan range
#           op = TxCheck    -- check upload patterns
#           op = TxDirty    -- scan for dirty uploads
#
#           TX-id           -- TX name e.g. DEMO4750, default 1st in list
#
#           record-count    -- DB depth to scan
#
#       access DB
#       scan for all TX in range
#       show TX reporting
#       show TX silent
#
###############################################################################
# import BleHealthSnapshot as bleHealthSnapshot
import BleModel as bleModel
import DbUtils as dbUtils
import math
import PlotUtils as plotUtils
import sys
import traceback

NADA = "nada"

COMMAND_LINE_OPTION_OP_HELP = "Usage: blescanner operation txname recordcount \nwhere op = txlist | txcheck | txmodel\nwhere recordcount = # DB records to scan, default=1000"

COMMAND_LINE_OPTION_OP_TXLIST = "txlist"
COMMAND_LINE_OPTION_OP_TXCHECK = "txcheck"
COMMAND_LINE_OPTION_OP_TXKEEP = "txkeep"
COMMAND_LINE_OPTION_OP_TXMODEL = "txmodel"

COMMAND_LINE_ARG_TXNAME_ALL = "*"
COMMAND_LINE_ARG_STARTRECORD_DEFAULT = 0
COMMAND_LINE_ARG_RECORDCOUNT_DEFAULT = 1000

COMMAND_LINE_ARG_OP = 1
COMMAND_LINE_ARG_TXNAME = 2
COMMAND_LINE_ARG_STARTRECORD = 3
COMMAND_LINE_ARG_RECORDCOUNT = 4

# flags
PANDA_ENABLED = False   # dump raw panda dataset
DISPLAY_BLESNAP_ENABLED = False
show_flag = False

###############################################################################
def main():

    # fetch command line options
    print("BleScanner command line ->")
    print(sys.argv, len(sys.argv))
    print(COMMAND_LINE_OPTION_OP_HELP)

    command_line_op = get_command_line_option(COMMAND_LINE_ARG_OP)
    command_line_txname = get_command_line_option(COMMAND_LINE_ARG_TXNAME)
    command_line_start_record = get_command_line_option(COMMAND_LINE_ARG_STARTRECORD)
    command_line_record_count = get_command_line_option(COMMAND_LINE_ARG_RECORDCOUNT)
    print("BleScanner op: ", command_line_op, ", TX name: ", command_line_txname, ", start record: ", str(command_line_start_record), ", record count: ", str(command_line_record_count))


    try:
        # open DB
        db_connection = dbUtils.openDb("US")
        # scan for unique TX
        tx_all_list, empty_row_count = dbUtils.getBleTx(db_connection, command_line_record_count)
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
        # tx_target_list.append("T0026654")
        # tx_target_list.append("DEMO4750")
        # tx_target_list.append("DEMO4119")
        # tx_target_list.append("T0026653")
        # tx_target_list.append("DEMO4906")
        # tx_target_list.append("DEMO1420")
        # tx_target_list.append("T0048094")
        # tx_target_list.append("DEMO3851")
        print("BleScanner target list: ", tx_target_list)

        # for each TX in target list
        tx_target_found = False
        for tx in tx_target_list:
            # if Tx target in all TX list
            if tx in tx_all_list:
                tx_target_found = True
                # generate datasets
                ble_snaps, df_collection, valid_row_count, empty_row_count, row_out_of_order, initial_interval_gap, interval_gap_count = \
                    dbUtils.getBleTxDataset(db_connection, command_line_start_record, command_line_record_count, tx, PANDA_ENABLED)
                if ble_snaps[0].isAndroid:
                    print("\n========= TX ", tx, " (Android) ==========")
                else:
                    print("\n========= TX ", tx, " (iOS) ==========")
                print("\ngetBleTxDataset row counts-> valid: " + str(valid_row_count) + ", empty: " + str(empty_row_count) + ", out of order: " + str(row_out_of_order))
                print("getBleTxDataset initial interval gap: " + str(math.trunc(initial_interval_gap)) + ", interval gap count: " + str(interval_gap_count) + "\n")
                # if enabled, dump raw data
                if PANDA_ENABLED:
                    print(df_collection.to_string())
                if DISPLAY_BLESNAP_ENABLED:
                    for snap in ble_snaps:
                        # print(snap.aTxName, ", ", snap.startTime, ", ", snap.stateChangeCount, ", ", snap.currentStateEnum)
                        # print(snap)
                        print(snap.toStateString())

                if command_line_op == COMMAND_LINE_OPTION_OP_TXMODEL:
                    # generate dataset shape & run alert model
                    txName, startDate, endDate, stateGraph, anyGraph = bleModel.modelAlerts(ble_snaps, show_flag)

                    # plot alert model
                    bleModel.plotAlerts(txName, startDate, endDate, stateGraph, anyGraph)

                # if panda enabled, display panda plots
                if PANDA_ENABLED:
                    plotUtils.drawBlePlot('currentStateIndex', df_collection, True)
                    plotUtils.drawBlePlot('aveDuration', df_collection)
                if command_line_op == COMMAND_LINE_OPTION_OP_TXKEEP:
                    plotUtils.drawBleKeepAlive(ble_snaps, df_collection)

        if not tx_target_found:
            print("Target TX ", tx_target_list, " not found in ", tx_all_list)
    except Exception as e:
        traceback.print_exc()
        print("Exception raised...exiting...")

    print("Tx Scan finito...")

###############################################################################
def get_command_line_option(arg):
    if len(sys.argv) > arg:
        option = sys.argv[arg]
    else:
        option = NADA

    if arg == COMMAND_LINE_ARG_OP:
        if option == COMMAND_LINE_OPTION_OP_TXLIST or \
            option == COMMAND_LINE_OPTION_OP_TXCHECK or \
            option == COMMAND_LINE_OPTION_OP_TXKEEP or \
            option == COMMAND_LINE_OPTION_OP_TXMODEL:
            return option
        else:
            return COMMAND_LINE_OPTION_OP_TXLIST

    if arg == COMMAND_LINE_ARG_TXNAME:
        if option == NADA:
            return COMMAND_LINE_ARG_TXNAME_ALL
        else:
            return option

    if arg == COMMAND_LINE_ARG_STARTRECORD:
        if option == NADA:
            return COMMAND_LINE_ARG_STARTRECORD_DEFAULT
        else:
            return option

    if arg == COMMAND_LINE_ARG_RECORDCOUNT:
        if option == NADA:
            return COMMAND_LINE_ARG_RECORDCOUNT_DEFAULT
        else:
            return option

    return NADA

###############################################################################
# launch main
if __name__ == "__main__":
    main()
###############################################################################
