###############################################################################
#   BleHealthViewer.MainTxScan
#       access DB
#       scan for all TX in range
#       show TX reporting
#       show TX silent
#
###############################################################################
# import BleHealthSnapshot as bleHealthSnapshot
import BleModel as alertUtils
import DbUtils as dbUtils
import PlotUtils as plotUtils
###############################################################################
def main():

    try:
        db_connection = dbUtils.openDb("US")

        record_count = 2000
        tx_all_list, empty_row_count = dbUtils.getBleTx(db_connection, record_count)
        print("TxScan all list: ", tx_all_list)
        print("TxScan empty row count: ", empty_row_count)

        panda_enabled = False
        raw_dump_enabled = True
        show_flag = True

        #    record_count = 2400
        tx_target_list = []
        # tx_target_list.append("T0026654")
        tx_target_list.append("DEMO4750")
        # tx_target_list.append("DEMO4119")
        # tx_target_list.append("T0026653")
        # tx_target_list.append("DEMO4906")
        # tx_target_list.append("DEMO1420")
        # tx_target_list.append("T0048094")
        # tx_target_list.append("DEMO3851")
        print("TxScan target list: ", tx_target_list)

        tx_target_found = False
        for tx in tx_target_list:
            if tx in tx_all_list:
                tx_target_found = True
                # generate datasets
                df_collection, ble_snaps = dbUtils.getBleTxDataset(db_connection, tx_target_list, record_count, panda_enabled)
                # if enabled, dump raw data
                if raw_dump_enabled:
                    if panda_enabled:
                        print(df_collection.to_string())
                    for snap in ble_snaps:
                        # print(snap.aTxName, ", ", snap.startTime, ", ", snap.stateChangeCount, ", ", snap.currentStateEnum)
                        # print(snap)
                        print(snap.toStateString())
                # generate dataset shape & run alert model
                txName, startDate, endDate, stateGraph, anyGraph = alertUtils.modelAlerts(ble_snaps, show_flag)

                # plot alert model
                alertUtils.plotAlerts(txName, startDate, endDate, stateGraph, anyGraph)
                # if panda enabled, display panda plots
                if panda_enabled:
                    plotUtils.drawBlePlot('currentStateIndex', df_collection, True)
                    plotUtils.drawBlePlot('aveDuration', df_collection)

        if not tx_target_found:
            print("Target TX ", tx_target_list, " not found in ", tx_all_list)
    except:
        print("Exception raised...exiting...")

    print("Tx Scan finito...")
###############################################################################
# launch main
if __name__ == "__main__":
    main()
###############################################################################
