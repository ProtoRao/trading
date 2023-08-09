from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import threading
import pyotp,time
import config
from datetime import datetime
import pandas as pd
import pandas_ta as ta
import os

# logging ----------------------------  #
import logging 
import sys 
td = datetime.today().date()
logging.basicConfig(filename=f"ANGEL_WEBSOCKET_{td}.log", format='%(asctime)s - %(levelname)s - %(message)s') 
  
  
logger=logging.getLogger() 
logger.setLevel(logging.INFO) 

stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)
  
# -------------------------#

def login():
    obj=SmartConnect(api_key=config.API_KEY)
    data = obj.generateSession(config.USERNAME,config.PIN,pyotp.TOTP(config.TOKEN).now())

    AUTH_TOKEN = data['data']['jwtToken']
    refreshToken= data['data']['refreshToken']
    FEED_TOKEN=obj.getfeedToken()
    res = obj.getProfile(refreshToken)
    logger.info(f'{res["data"]["products"]}')
    
    sws = SmartWebSocketV2(AUTH_TOKEN, config.API_KEY, config.USERNAME, FEED_TOKEN ,max_retry_attempt=5)
    return obj, sws


#------- Websocket code ---------#

def on_data(wsapp, msg):
    try:
        global df2,tf,a
        result_dict={key: msg[key] for key in config.KEYS if key in msg}
        result_dict['last_traded_price']/=100.0
        result_dict['exchange_timestamp'] = datetime.fromtimestamp(result_dict['exchange_timestamp']/1000)
        new_row=list(result_dict.values())
        new_row.extend(list(datetime.now(config.TIME_ZONE).timetuple())[3:6])
        ii = config.TIMEDICT[str(new_row[-3])+':'+str(tf*int(new_row[-2]/tf))]
        if new_row[-2]%tf==0 and new_row[-1]==0 and ii>0:
            df2.at[ii,'Open']  = result_dict['last_traded_price']
            df2.at[ii-1,'Close'] = result_dict['last_traded_price']
        if ii==0:
            df2.at[ii,'Open']  = result_dict['last_traded_price']
        if result_dict['last_traded_price']>df2.loc[ii,'High']:
            df2.at[ii,'High'] = result_dict['last_traded_price']
        if result_dict['last_traded_price']<df2.loc[ii,'Low']:
            df2.at[ii,'Low'] = result_dict['last_traded_price']
        if ii>0:
            df2.at[ii,'Supertrend'] = ta.supertrend(df2['High'][:ii], df2['Low'][:ii], df2['Close'][:ii],length=1,multiplier=2)['SUPERT_1_2.0'].values[-1]
        os.system('cls')
        print(df2.to_string())

    except Exception as e:
        #print('Error at on_data ',e)
        pass

def on_error(wsapp, error):
    logger.error(f"---------Connection Error {error}-----------")

def on_close(wsapp):
    logger.info("---------Connection Close-----------")

def close_connection(sws):
    sws.MAX_RETRY_ATTEMPT = 0
    sws.close_connection()

def subscribeSymbol(token_list,sws):
    sws.subscribe(config.CORRELATION_ID, config.FEED_MODE, token_list)

def connectFeed(sws,tokeList = None):  
    def on_open(wsapp):
        logger.info("on open")
    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close
    threading.Thread(target =sws.connect,daemon=True).start()

if __name__ == "__main__":
    config.SMART_API_OBJ , config.SMART_WEB = login()
    df = pd.DataFrame(columns=config.KEYS)
    df2 = pd.DataFrame(columns=['Time','Open','High','Low','Close','Supertrend'])
    df2['Time'] = config.TIMELIST
    df2['High'] = [0.0]*len(df2)
    df2['Open'] = [0.0]*len(df2)
    df2['Close'] = [0.0]*len(df2)
    df2['Supertrend'] = [0.0]*len(df2)
    df2['Low']  = [2e5]*len(df2)
    tf=5
    connectFeed(config.SMART_WEB)
    time.sleep(1)
    subscribeList  = [{"exchangeType": 1, "tokens": ["99926000"]}]
    starttime=[12,15,0]

    while (True):
        if list(datetime.now(config.TIME_ZONE).timetuple())[3:6]==starttime:
            break
        os.system('cls')
        print('Waiting for Day Start at {}:{}'.format(starttime[0],starttime[1]))
        print('Current Time {}:{}'.format(list(datetime.now(config.TIME_ZONE).timetuple())[3],list(datetime.now(config.TIME_ZONE).timetuple())[4]))
        time.sleep(0.1)

    subscribeSymbol(subscribeList,config.SMART_WEB)

    while(list(datetime.now(config.TIME_ZONE).timetuple())[3:6]!=[15,15,0]):
        time.sleep(1)

    close_connection(config.SMART_WEB)
    logger.info("Connection closed")
    time.sleep(1)
    logger.info("-----------Exit----------")






































