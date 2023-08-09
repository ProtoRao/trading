
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger
from SmartApi import SmartConnect #or from smartapi.smartConnect import SmartConnect
import xlwings as xw
import pandas as pd
import pandas_ta as ta
import pyotp
import requests

def fetch_nse_data(company_name):
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    response = requests.get(url,params={})
    nse_companies_data = response.json()
    for company_data in nse_companies_data:    
        if(company_data['symbol'] == company_name):
            print('found')
            return company_data


fetch_nse_data('NIFTY')
obj=SmartConnect(api_key="I3K6t4CS")
data = obj.generateSession("K51179152","0852",pyotp.TOTP("P3DKV5OFUK5JG6GDI5SVENU4IM").now())

AUTH_TOKEN = data['data']['jwtToken']
API_KEY = "I3K6t4CS"
CLIENT_CODE = "K51179152"
FEED_TOKEN = obj.getfeedToken()
correlation_id = "abc123"
action = 1
mode = 1

token_list = [
    {
        "exchangeType": 1,
        "tokens": ["26000"]
    }
]

sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

def on_data(wsapp, message):
    print("Ticks: {}".format(message))
    # if message == '':
    close_connection()
    # close_connection()

def on_open(wsapp):
    print("on open")
    sws.subscribe(correlation_id, mode, token_list)
    # sws.unsubscribe(correlation_id, mode, token_list1)


def on_error(wsapp, error):
    #print('Error Found')
    print(error)


def on_close(wsapp):
    print("Close")


def close_connection():
    sws.close_connection()

sws.HEART_BEAT_INTERVAL = 1
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

sws.connect()



