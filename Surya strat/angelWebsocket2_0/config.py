import pytz
from datetime import datetime
TIME_ZONE = pytz.timezone('Asia/Kolkata')
TZ_INFO = datetime.now(TIME_ZONE).tzinfo
TIME = list(datetime.now(TIME_ZONE).timetuple())

API_KEY  =  'I3K6t4CS'
USERNAME =  'K51179152'
PIN      =  '0852'
TOKEN    =  'P3DKV5OFUK5JG6GDI5SVENU4IM'
KEYS  = ['subscription_mode','token','exchange_timestamp', 'last_traded_price','Hours','Minutes','Seconds']
KEYS1 = ['subscription_mode', 'exchange_type', 'token', 'sequence_number', 'exchange_timestamp', 'last_traded_price', 'subscription_mode_val']
KEYS2 = ['subscription_mode', 'exchange_type', 'token', 'sequence_number', 'exchange_timestamp', 'last_traded_price', 'subscription_mode_val', 'last_traded_quantity', 'average_traded_price', 'volume_trade_for_the_day', 'total_buy_quantity', 'total_sell_quantity', 'open_price_of_the_day', 'high_price_of_the_day', 'low_price_of_the_day', 'closed_price', 'last_traded_timestamp', 'open_interest', 'open_interest_change_percentage', 'upper_circuit_limit', 'lower_circuit_limit', '52_week_high_price', '52_week_low_price']
#TIMELIST = ['9:15', '9:30', '9:45', '10:0', '10:15', '10:30', '10:45','11:0', '11:15', '11:30', '11:45', '12:0', '12:15', '12:30','12:45', '13:0', '13:15', '13:30', '13:45', '14:0', '14:15','14:30', '14:45', '15:0']
#TIMEDICT = dict(zip(TIMELIST, list(range(len(TIMELIST)))))

SMART_API_OBJ = None
LIVE_FEED_JSON = {}
SMART_WEB = None
CORRELATION_ID = 'abc123'  # ANY random string
FEED_MODE = 1

TIMELIST=[]
with open('listfile.txt', 'r') as filehandle:
    for line in filehandle:
        TIMELIST.append(line[:-1])

TIMEDICT = dict(zip(TIMELIST, list(range(len(TIMELIST)))))