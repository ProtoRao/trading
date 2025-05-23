# package import statement
from SmartApi import SmartConnect #or from smartapi.smartConnect import SmartConnect
import xlwings as xw
import pandas as pd
# import talib as ta
import pyotp



#import smartapi.smartExceptions(for smartExceptions)

#create object of call
obj=SmartConnect(api_key="I3K6t4CS")

#login api call

data = obj.generateSession("K51179152","0852",pyotp.TOTP("P3DKV5OFUK5JG6GDI5SVENU4IM").now())

refreshToken= data['data']['refreshToken']

#fetch the feedtoken
feedToken=obj.getfeedToken()
print(feedToken)

authToken=data['data']['jwtToken']
print(authToken)

#fetch User Profile
userProfile= obj.getProfile(refreshToken)
#place order
try:
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": "3045",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "19500",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "1"
        }
    orderId=obj.placeOrder(orderparams)
    print("The order id is: {}".format(orderId))
except Exception as e:
    print("Order placement failed: {}".format(e.message))

"""
#gtt rule creation
try:
    gttCreateParams={
            "tradingsymbol" : "SBIN-EQ",
            "symboltoken" : "3045",
            "exchange" : "NSE", 
            "producttype" : "MARGIN",
            "transactiontype" : "BUY",
            "price" : 100000,
            "qty" : 10,
            "disclosedqty": 10,
            "triggerprice" : 200000,
            "timeperiod" : 365
        }
    rule_id=obj.gttCreateRule(gttCreateParams)
    print("The GTT rule id is: {}".format(rule_id))
except Exception as e:
    print("GTT Rule creation failed: {}".format(e.message))
    
#gtt rule list
try:
    status=["FORALL"] #should be a list
    page=1
    count=10
    lists=obj.gttLists(status,page,count)
except Exception as e:
    print("GTT Rule List failed: {}".format(e.message))
"""

#Historic api
try:
    historicParam={
    "exchange": "NSE",
    "symboltoken": "3045",
    "interval": "ONE_MINUTE",
    "fromdate": "2021-02-08 09:00", 
    "todate": "2021-02-08 09:16"
    }
    obj.getCandleData(historicParam)
except Exception as e:
    print("Historic Api failed: {}".format(e.message))

"""
#logout
try:
    logout=obj.terminateSession('K51179152')
    print("Logout Successfull")
except Exception as e:
    print("Logout failed: {}".format(e.message))
"""


## WebSocket

#from SmartApi.webSocket import WebSocket

from SmartApi.smartWebSocketV2 import SmartWebSocketV2

FEED_TOKEN= feedToken
CLIENT_CODE="K51179152"
AUTH_TOKEN= authToken
API_KEY="I3K6t4CS"
token="nse_cm|3045" #"nse_cm|2885&nse_cm|1594&nse_cm|11536"
task="mw" #"mw"|"sfi"|"dp"
ss = SmartWebSocketV2( AUTH_TOKEN, API_KEY, CLIENT_CODE,FEED_TOKEN ,1)

def on_tick(ws, tick):
    print("Ticks: {}".format(tick))

def on_connect(ws, response):
    ws.websocket_connection() # Websocket connection  
    ws.send_request(token,task) 
    
def on_close(ws, code, reason):
    ws.stop()

# Assign the callbacks.
ss.on_ticks = on_tick
ss.on_connect = on_connect
ss.on_close = on_close

ss.connect()


