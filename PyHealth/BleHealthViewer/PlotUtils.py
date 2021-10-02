###############################################################################
#   BleHealthViewer.PlotUtils
#
#   Created from TinLatt by MatthewTucker on 09MAY19.
###############################################################################
from datetime import datetime
import json
import os
import sys


import pymssql as pymssql
import pytz as pytz
#from pip._internal.utils import logging

import matplotlib.pyplot as plt
import pandas as pd

###############################################################################
def drawBlePlot(type, Df, show_flag):
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
    if (show_flag):
        plt.show()
    print('')

def drawBleKeepAlive(ble_snaps, df_collection):
    return True

###############################################################################
