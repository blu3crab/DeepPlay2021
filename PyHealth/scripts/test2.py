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
    region = "OUS"

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
            database="DB_EversenseDMS_3.0",
            user="sens04dbstaging",
            server="46.17.89.55",
            password="uqf!+4yD!x8U%jCx"
        )
    # endregion
    print("db connection is GOOD!")

except:
    print("I am unable to connect to the database")
    raise

def getblebeats1():
    try:
        fig = plt.figure()
        ax1 = plt.subplot2grid((1, 1), (0, 0))

        cur = conn.cursor()
        sql = """exec sp_Tableau_BleStateView {0}""".format(50)
        # sql = """exec [sp_JsonToViewColor] 3"""
        cur.execute(sql)
        rows = cur.fetchall()
        auditDate = []
        status=[]
        aTxName=[]
        x=[]
        # jsonStr = json.loads(data)
        prevTxName=''
        for row in rows:

            currTxName = row[2]
            if prevTxName == '':
                prevTxName=currTxName
            else:
                if currTxName != prevTxName:
                    #plot legend and reset
                    ax1.plot(auditDate,status,label=prevTxName)
                    auditDate.clear()
                    status.clear()
                    aTxName.clear()

            auditDate.append(str(row[0].hour)+':'+str(row[0].minute))
            status.append(row[1])
            aTxName.append(row[2])
            prevTxName = currTxName

            # foo = json.loads(row[0])
            # # foo = row[1]
            # print(foo['startTime'])
            #
            # # get time in tz
            # tz = pytz.timezone('America/New_York')
            # dt = datetime.fromtimestamp(foo['startTime']/1000, tz)
            # # print it
            # print(dt.strftime('%Y-%m-%d %H:%M:%S %Z%z'))
            #
            # x.append(dt.strftime('%Y-%m-%d %H:%M:%S %Z%z'))
            # currentStateIndex.append(foo['currentStateIndex'])
            # keepAliveCount.append(foo['keepAliveCount'])


        conn.commit()
        cur.close()



        # keepAliveCountBins=[0,7,15,25]
        # ax1.plot(x,currentStateIndex,label='currentStateIndex')
        # ax1.bar(x,keepAliveCount,label='keepAliveCount',color='r')
        # plt.hist(keepAliveCount,keepAliveCountBins,histtype='bar',rwidth=0.8,label='keepAliveCountHistogram')
        #
        # plt.xlabel('time')
        # plt.ylabel('ble state\n 0=blaa, 1 =blah')
        # plt.title('graph for mat')
        # plt.legend()
        for foo in ax1.xaxis.get_ticklabels():
            foo.set_rotation(90)
        plt.legend()
        plt.show()
        return x

    except Exception as e:
        logging.debug('ERRRRR')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.debug(exc_type, fname, exc_tb.tb_lineno)
        pass

def getblebeats(txarray,recordcount):
    try:
        cur = conn.cursor()
        sql = """select top {0} comment from audit order by createddate desc""".format(recordcount)
        # sql = """exec [sp_JsonToViewColor] 3"""
        cur.execute(sql)
        rows = cur.fetchall()
        x = []
        currentStateIndex=[]
        keepAliveCount=[]

        # jsonStr = json.loads(data)
        # df = pd.read_json(rows)
        for row in rows:
            foo = json.loads(row[0])
            # foo = row[1]
            print(foo['startTime'])

            # get time in tz
            tz = pytz.timezone('America/New_York')
            dt = datetime.fromtimestamp(foo['startTime']/1000, tz)
            # print it
            print(dt.strftime('%Y-%m-%d %H:%M:%S %Z%z'))

            x.append(dt.strftime('%Y-%m-%d %H:%M:%S %Z%z'))
            currentStateIndex.append(foo['currentStateIndex'])
            keepAliveCount.append(foo['keepAliveCount'])


        conn.commit()
        cur.close()

        fig = plt.figure()
        ax1=plt.subplot2grid((1,1),(0,0))

        keepAliveCountBins=[0,7,15,25]
        # ax1.plot(x,currentStateIndex,label='currentStateIndex')
        ax1.bar(x,keepAliveCount,label='keepAliveCount',color='r')
        # plt.hist(keepAliveCount,keepAliveCountBins,histtype='bar',rwidth=0.8,label='keepAliveCountHistogram')

        plt.xlabel('time')
        plt.ylabel('ble state\n 0=blaa, 1 =blah')
        plt.title('graph for mat')
        plt.legend()
        for foo in ax1.xaxis.get_ticklabels():
            foo.set_rotation(45)
        plt.show()
        return x

    except Exception as e:
        logging.debug('ERRRRR')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.debug(exc_type, fname, exc_tb.tb_lineno)
        pass

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
                Df = Df.append(df)
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
    Df['keepAliveTimeTicker']=pd.to_datetime((Df['keepAliveTimeTicker']/1000)-18000,unit='s')
        # .dt.tz_localize('UTC').tz_convert('US/Eastern')
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
    print('hey')
    # print(getblebeats(None,50))
    # print(getblebeats1())
    Tx = getBleTx(3)
    print(Tx)
    Df = getBleTxDataset(Tx,200)
    print(Df)
    # drawBlePlot('currentStateIndex', Df)
    drawBlePlot('aveDuration', Df)





