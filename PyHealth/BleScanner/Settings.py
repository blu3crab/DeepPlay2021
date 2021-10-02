###############################################################################
#   Settings
#       module scoped constants
###############################################################################
# trace levels
DEBUG = False
INFO = True
WARNING = True
ERROR = True
CRITICAL = True

###############################################################################
# DB servers
OUS_STAGING = 'OUS Staging'
US_STAGING = 'US Staging'
US_PRODUCTION_COPY = "US Production Copy"
###############################################################################
# alert modeling
ALERT_COLOR_ENUM = ['GREEN', 'YELLOW', 'RED', 'GRAY']
# alert color names
ALERT_COLOR_GREEN = 'GREEN'
ALERT_COLOR_YELLOW = 'YELLOW'
ALERT_COLOR_RED = 'RED'
ALERT_COLOR_GRAY = 'GRAY'
# alert indices
ALERT_INDEX_GREEN = 0
ALERT_INDEX_YELLOW = 1
ALERT_INDEX_RED = 2
ALERT_INDEX_GRAY = 3

# discontinuity if end of upload interval and start of next upload interval exceeds fudge
DISCONTINUITY_DURATION_FUDGE = 2000
# disconnect high water marks
RED_HIGH_WATER_MARK_DISCONNECT_DURATION = 5
YELLOW_HIGH_WATER_MARK_DISCONNECT_DURATION = 3
# state change high water marks
RED_HIGH_WATER_MARK_STATE_CHANGE = 8
YELLOW_HIGH_WATER_MARK_STATE_CHANGE = 5
# upload interval high water marks
RED_HIGH_WATER_MARK_UPLOAD_INTERVAL = 30
YELLOW_HIGH_WATER_MARK_UPLOAD_INTERVAL = 18

# keep alive high water marks
IDEAL_KEEPALIVE_INTERVAL = 60000
YELLOW_KEEPALIVE_INTERVAL = 10000
RED_KEEPALIVE_INTERVAL = 180000

###############################################################################