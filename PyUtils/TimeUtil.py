__author__ = "blu3crab"
__license__ = "Apache License 2.0"
__version__ = "0.0.1"

# Timedelta function demonstration
from datetime import datetime, timedelta

def getDateTime(print_result=False):
    # get start time
    now_time = datetime.now()
    if (print_result): print("now time->", str(now_time))
    return now_time
#
# # Some another datetime
# new_final_time = start_time + \
#                  timedelta(days=2)

def getElapsedTime(start_time, end_time, print_result=False):
    # set elapsed time
    elapsed_time = end_time - start_time
    if (print_result): print("elapsed time->", str(elapsed_time))
