###############################################################################
#   DbUtils
#       openDb      -- open DB for region
#           def openDb(region):
#               return conn
#       getBleTx    -- fetch list of TX in DB
#           def getBleTx(conn, record_count):
#               return tx_list, empty_row_count
#       getBleTxDataset -- fetch datasets associated with TX
#           def getBleTxDataset(conn, start_record, record_count, txname, panda_enabled):
#               return bleSnaps, df_collection, valid_row_count, empty_row_count, row_out_of_order, initial_interval_gap, interval_gap_count
#
#   Created from TinLatt by MatthewTucker on 09MAY19.
###############################################################################
from datetime import datetime
import json
import math
import os
import pandas as pd
import pymssql as pymssql
import pyodbc
import sys
import time
import traceback

import BleHealthSnapshot as bleHealthSnapshot
import BleCheck as bleCheck
import Settings

# flags
PRINT_INVALID_TIME_ORDER = False           # dump out of order rows
###############################################################################

def openDb(db_server):
    # DB server:
    #   OUS_STAGING = 'OUS Staging'
    #   US_STAGING = 'US Staging'
    #   US_PRODUCTION_COPY = "US Production Copy"
    conn = 0
    try:
        # get connection to OUS
        if db_server == Settings.OUS_STAGING:
            conn = pymssql.connect(
                database="DB_EversenseDMS_3.0",
                user="sens04dbstaging",
                server="46.17.89.55",
                password="uqf!+4yD!x8U%jCx"
            )

        # get connection to US
        elif db_server == Settings.US_STAGING:
            conn = pyodbc.connect(
                'DRIVER={ODBC Driver 13 for SQL Server};SERVER=10.138.0.75;DATABASE=DB_EversenseDMS_3.0_Staging;UID=sens04dbuser;PWD=Sp%arE=-ZPpd67tq')
            # conn = pymssql.connect(
            #     database="DB_EversenseDMS_3.0_Staging",
            #     user="sens04dbuser",
            #     server="10.138.0.75\MSSQL",
            #     password="Sp%arE=-ZPpd67tq"
            # )

        elif db_server == Settings.US_PRODUCTION_COPY:
            conn = pymssql.connect(
                database="US_EversenseDMS_3.0_Production",
                user="dbuser",
                server="92wx0n2",
                password="sense0n1cs"
            )

        print("DbUtils: DB connection to ", db_server)
        return conn

    except:
        print("DbUtils: NO db connection to ", db_server)
        raise

###############################################################################
# getBleTx -- get list of unique TX in DB
#       conn -- DB connection
#       record_count -- # records in DB to scan
#
#   returns
#       tx_list -- list of unique TX in DB scan range
#       empty_row_count -- empty rows in DB scan range
def getBleTx(conn, record_count):
    try:
        cur = conn.cursor()
        sql = """select top {0} comment from audit order by createddate desc""".format(record_count)
        cur.execute(sql)
        rows = cur.fetchall()
        tx_list = []
        empty_row_count = 0

        for row in rows:
            jsonStr = row[0]
            if jsonStr != None:
                # test if valid JSON snapshot
                valid, tx, jsonObj = isTxInJsonString(jsonStr)
                # add TX to list if valid & not already in list
                if valid and tx != '' and tx not in tx_list:
                    tx_list.append(tx)
            else:
                # print("getBleTx skipping empty row...")
                empty_row_count = empty_row_count + 1

            conn.commit()
        cur.close()
        return tx_list, empty_row_count

    except Exception as e:
        traceback.print_exc()
        print("getBleTx -> Exception raised...")
###############################################################################
#   getBleTxDataset -- get BLE health, (optionally) Panda dataset of selected TX
#       conn -- DB connection
#       record_count -- # records in DB to scan
#       txname -- TX of interest
#       panda_enabled -- flag set True if Panda dataframe should be generated
#
#   returns
#       ble_snaps -- list of BleHealthSnapshots
#       df_collection -- Panda dataframe of selected snapshots (optional)

def getBleTxDataset(conn, start_record, record_count, txname, start_time, end_time, panda_enabled):
    try:
        print("\n")
        cur = conn.cursor()
        # sql = """select top {0} comment from audit order by createddate desc""".format(record_count)

        # # tx_sql_string = "'%" + tx_list[0] + "%'"
        # tx_sql_string = "\'%DEMO4750%\'"
        tx_sql_string = "\'%" + txname + "%\'"
        # print(txname)
        # sql = """select top {0} comment from audit where comment like {1} order by createddate desc""".format(record_count, tx_sql_string)
        sql = """select top {0} comment from audit where comment like {1} order by AuditDate desc""".format(record_count, tx_sql_string)
        print(sql)
        cur.execute(sql)
        # sql = """select top {0} from audit where comment like (%s) order by createddate desc""".format(recordCount)
        # print(sql)
        # cur.execute(sql, [tx_sql_string])
        rows = cur.fetchall()

        df_collection = pd.DataFrame()          # panda dataframe collection of filtered DB query results
        bleSnaps = []                           # BleHealthSnapshot collection of filtered DB query results
        prevTimeMs = 0                            # most recent keep alive time ticker
        prevJsonObj = None
        row_counter = 0
        valid_row_count = 0
        invalid_row_count = 0
        out_of_range_count = 0
        row_out_of_order = 0
        empty_row_count = 0
        interval_gap_count = 0
        interval_nonideal_count = 0
        keepalive_nonideal_count = 0
        # for each row containing a BleHealth snapshot in JSON format
        for row in rows:
            jsonStr = row[0]
            # exclude empty rows
            if jsonStr != None:
                # convert JSON string to JSON object (test if valid JSON snapshot)
                valid, tx, jsonObj = isTxInJsonString(jsonStr)

                if valid:
                    if row_counter >= int(start_record) and row_counter < int(record_count):
                        # determine if valid time order (descending from most recent to least recent)
                        valid, time_ticker = bleCheck.isTimeOrdered(jsonObj, prevJsonObj)
                        # if valid time ordering
                        if valid:
                            within_range = bleCheck.isWithinRange(jsonObj, start_time, end_time)

                            if within_range:
                                # build panda dataframe if flagged
                                if panda_enabled:
                                    df = pd.read_json(jsonStr)
                                    df_collection = df_collection.append(df, sort=True)
                                # build lsit of BleHealthSnapshots
                                snap = bleHealthSnapshot.BleHealthSnapshot(jsonObj)
                                bleSnaps.append(snap)
                                # print(snap.toString())

                                # check if state transition durations are reasonable
                                if snap.isIntervalValid() == False:
                                    interval_nonideal_count = interval_nonideal_count + 1
                                    # print("getBleTxDataset finds ", str(interval_nonideal_count), " non-ideal intervals")
                                # check if keep alive counts are reasonable
                                if snap.isKeepAliveCountValid() == False:
                                    keepalive_nonideal_count = keepalive_nonideal_count + 1
                                    # print("getBleTxDataset finds ", str(keepalive_nonideal_count), " non-ideal keep alive counts.")
                            else:
                                # out of range
                                out_of_range_count = out_of_range_count + 1
                        else:
                            # 2nd row is discarded (often a dup several millisecs after 1st, occasionally slightly behind the 1st row)
                            row_out_of_order = row_out_of_order + 1
                            if PRINT_INVALID_TIME_ORDER:
                                print("getBleTxDataset invalid time order counter ", row_out_of_order, " of total rows ", valid_row_count, "\n")
                                print("prev row(", row_counter-1, "): ", prevJsonStr)
                                print("curr row(", row_counter, "): ", jsonStr)
                                # print("getBleTxDataset invalid time order for row(", row_counter, ") with prevTimeMs(", prevTimeMs, "): ", jsonStr)

                        # if first valid row
                        if valid_row_count == 0:
                            # get current time
                            currentTimeMs = bleCheck.getMillis()
                            # print("getBleTxDataset current ms ", currentTimeMs)
                            # determine if most recent upload is within interval (interval_gap=0)
                            # initial_interval_gap = getIntervalGap(currentTimeMs, keepAliveTimeTicker)
                            initial_interval_gap = bleCheck.getIntervalGap(currentTimeMs, time_ticker)
                            if initial_interval_gap > 1:
                                print(">>>getBleTxDataset finds INITIAL interval gap of ", math.trunc(initial_interval_gap), " (", initial_interval_gap/4, " hrs)")
                                interval_gap_count = interval_gap_count + 1
                        else:
                            interval_gap = bleCheck.getIntervalGap(time_ticker, prevTimeMs)
                            if interval_gap > 1:
                                print(">>>getBleTxDataset finds interval gap of ", math.trunc(interval_gap), " (", interval_gap/4, " hrs)", " at row ", row_counter)
                                interval_gap_count = interval_gap_count + math.trunc(interval_gap)
                        # retain previous row info
                        prevJsonObj = jsonObj
                        prevJsonStr = jsonStr
                        prevTimeMs = time_ticker
                        # bump valid row counter
                        valid_row_count = valid_row_count + 1
                    else:
                        print("getBleTxDataset skipping out of range row ", row_counter)
                else:
                    #print("getBleTx skipping empty row...")
                    invalid_row_count = invalid_row_count + 1

            else:
                #print("getBleTx skipping empty row...")
                empty_row_count = empty_row_count + 1
            # bump row counter
            row_counter = row_counter + 1

        print("\n", "getBleTxDataset invalid time order counter ", row_out_of_order, " of total rows ", valid_row_count)
        print("getBleTxDataset finds ", str(interval_nonideal_count), " non-ideal intervals")
        print("getBleTxDataset finds ", str(keepalive_nonideal_count), " non-ideal keep alive counts.")
        print("getBleTxDataset finds ", str(out_of_range_count), " rows outside time range.")

        conn.commit()
        cur.close()
        return bleSnaps, df_collection, valid_row_count, empty_row_count, row_out_of_order, initial_interval_gap, interval_gap_count

    except Exception as e:
        traceback.print_exc()
        print("getBleTxDataset -> Exception raised...")


###############################################################################
# isTxInJsonString
#       input JsonStr from jsonObj
#           {"aTxName":"T0026653","aveDuration":[9669,0,0,0,12253,0],"aveKeepAlive":59801,"currentStateEnum":"CONNECTED","currentStateIndex":5,"keepAliveCount":1226,"keepAliveTimeTicker":1557942713862,"maxDuration":[18760,0,0,0,12253,0],"maxKeepAlive":60265,"minDuration":[579,0,0,0,12253,0],"minKeepAlive":27851,"mobileId":"e8e3b7734f9f4aa1","startTime":1557869163580,"stateChangeCount":[2,0,0,0,1,0],"stateTimeTicker":1557869195172,"txSerialNo":"26653","version":"1A"}
#       returns
#               success flag - true if valid JSON found
#               TX name - TX name in JSON
#               JSON object
def isTxInJsonString(jsonStr):
    try:
        jsonObj = json.loads(jsonStr)
        tx = jsonObj['aTxName']
        return True, tx, jsonObj

    except Exception as e:
        print("isTxInJsonString exception for invalid JSON: ", jsonStr)
        return False, "nada", None
###############################################################################
# isTxInJsonString
#       input JsonStr
#           {"aTxName":"T0026653","aveDuration":[9669,0,0,0,12253,0],"aveKeepAlive":59801,"currentStateEnum":"CONNECTED","currentStateIndex":5,"keepAliveCount":1226,"keepAliveTimeTicker":1557942713862,"maxDuration":[18760,0,0,0,12253,0],"maxKeepAlive":60265,"minDuration":[579,0,0,0,12253,0],"minKeepAlive":27851,"mobileId":"e8e3b7734f9f4aa1","startTime":1557869163580,"stateChangeCount":[2,0,0,0,1,0],"stateTimeTicker":1557869195172,"txSerialNo":"26653","version":"1A"}
#       returns success flag, TX name, json object
# def isTxInJsonString(jsonStr):
#     try:
#         jsonObj = json.loads(jsonStr)
#         tx = jsonObj['aTxName']
#         return True, tx, jsonObj
#
#     except Exception as e:
#         print("isTxInJsonString Exception for: ", jsonStr)
#         return False, "nada", None
# ###############################################################################
# # isTimeDescending
# TIME_TICKER_LABEL = bleHealthSnapshot.TIME_TICKER_LABEL
# # TIME_TICKER_LABEL = 'keepAliveTimeTicker'
# def isTimeOrder(jsonObj, prevTime):
#     try:
#         # extract keep alive ticker
#         time_ticker = jsonObj[TIME_TICKER_LABEL]
#         # if time descending, correct most recent to oldest order
#         if time_ticker < prevTime:
#             return True, time_ticker
#         else:
#             # if first pass, assign time
#             if prevTime == 0:
#                 return True, time_ticker
#             else:
#                 # invalid time order
#                 return False, time_ticker
#
#     except isTimeOrder as e:
#         print("isTimeOrder Exception for: ", time_ticker)
#         return False, 0

# ###############################################################################
# # get current milliseconds
# def getMillis():
#     # local time!
#     # dt = datetime.now()
#     # ms = (dt.day * 24 * 60 * 60 + dt.second) * 1000 + dt.microsecond / 1000
#     # print(dt.date(), ", ms ", ms)
#
#     # get UTC milliseconds
#     ms = int(round(time.time() * 1000))
#     # print("getMillis: UTC ",ms, " ms")
#     return ms
#
# ###############################################################################
# # get interval gap between snapshots
# def getIntervalGap(currentTimeMs, prevTimeMs):
#     interval_gap = (currentTimeMs - prevTimeMs) / bleHealthSnapshot.BleHealthSnapshot.DURATION_IDEAL_MS
#     return interval_gap
###############################################################################
