from datetime import datetime
import json
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd


import pymssql as pymssql
import pytz as pytz
from pip._internal.utils import logging

try:
    #region could be "US" or "OUS"
    region = "US"

    #region connection to OUS
    if region == "OUS":
        conn = pymssql.connect(
            database="DB_EversenseDMS_3.0",
            user="sens04dbstaging",
            server="46.17.89.55",
            password="uqf!+4yD!x8U%jCx"
        )
    #endregion

    # region connection to OUS
    if region == "US":
        conn = pymssql.connect(
            database="DB_EversenseDMS_3.0_Staging",
            user="sens04dbuser",
            server="10.138.0.75",
            password="Sp%arE=-ZPpd67tq"
        )
    # endregion
    print("db connection is GOOD!")

except:
    print("I am unable to connect to the database")
    raise


def getBleTx(recordCount):
    try:
        cur = conn.cursor()
        sql = """select top {0} comment from audit order by createddate desc""".format(recordCount)
        cur.execute(sql)
        rows = cur.fetchall()
        Tx = []

        for row in rows:
            foo = json.loads(row[0])
            tx = foo['aTxName']
            if tx not in Tx and tx != None and tx != '':
                Tx.append(tx)
        conn.commit()
        cur.close()
        return Tx

    except Exception as e:
        logging.debug('ERRRRR')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.debug(exc_type, fname, exc_tb.tb_lineno)
        pass

def getBleTxDataset(Tx,recordCount):
    try:
        cur = conn.cursor()
        sql = """select top {0} comment from audit order by createddate desc""".format(recordCount)
        cur.execute(sql)
        rows = cur.fetchall()
        Df =pd.DataFrame()
        for row in rows:
            jsonStr = row[0]
            jsonObj = json.loads(jsonStr)
            tx = jsonObj['aTxName']
            if tx in Tx:
                df = pd.read_json(jsonStr)
                Df = Df.append(df,sort=True)
            # foo = json.loads(row[0])
            # tx = foo['aTxName']
            # if tx not in Tx and tx != None and tx != '':
            #     Tx.append(tx)
        conn.commit()
        cur.close()
        return Df

    except Exception as e:
        logging.debug('ERRRRR')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.debug(exc_type, fname, exc_tb.tb_lineno)
        pass

def drawBlePlot(type,Df):
    fig = plt.figure()
    ax1 = plt.subplot2grid((1, 1), (0, 0))
    Df['keepAliveTimeTicker']=pd.to_datetime((Df['keepAliveTimeTicker']/1000),unit='s').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    Df.keepAliveTimeTicker = Df.keepAliveTimeTicker.dt.time
    Df = Df[['keepAliveTimeTicker', type, 'aTxName']]
    DfTx = Df[['aTxName']].drop_duplicates()
    Df = Df[['keepAliveTimeTicker', type, 'aTxName']].drop_duplicates()

    for foo in DfTx:
        print(foo)
    for i in range(0,len(DfTx)):
        aTxName = DfTx.iloc[i][0]
        Dfnew = Df[Df['aTxName']==aTxName]
        x = Dfnew['keepAliveTimeTicker']
        y = Dfnew[type]
        # ax1.invert_xaxis()
        ax1.plot(x, y, label=aTxName)
    # plt.ylim(0, 6)
    plt.xlabel('time')
    plt.ylabel(type)
    plt.title(type+ ' graph')
    plt.legend()
    for foo in ax1.xaxis.get_ticklabels():
        foo.set_rotation(90)
        foo.set_fontsize(10)
    plt.show()
    print('')



if __name__ == "__main__":
    Tx = getBleTx(100)
    print(Tx)
    # Tx = ['T0026653']
    Df = getBleTxDataset(Tx,200)
    drawBlePlot('currentStateIndex', Df)
    # drawBlePlot('aveDuration', Df)






