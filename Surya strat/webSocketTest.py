from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import threading
import pyotp,time
import  config
from datetime import datetime

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
    #print(data)
    AUTH_TOKEN = data['data']['jwtToken']
    refreshToken= data['data']['refreshToken']
    FEED_TOKEN=obj.getfeedToken()
    res = obj.getProfile(refreshToken)
    logger.info(f'{res["data"]["products"]}')
    
    sws = SmartWebSocketV2(AUTH_TOKEN, config.API_KEY, config.USERNAME, FEED_TOKEN ,max_retry_attempt=5)
    return obj, sws


#------- Websocket code


def on_data(wsapp, msg):
    try:
        print("Ticks: {}".format(msg))
        #config.LIVE_FEED_JSON[msg['token']] = {'token' :msg['token'] , 'ltp':msg['last_traded_price']/100 , 'exchange_timestamp':  datetime.fromtimestamp(msg['exchange_timestamp']/1000,config.TZ_INFO)}
        #print(config.LIVE_FEED_JSON ,"\n \n ")
        #if datetime.now().second < 1:
            #logger.info(f"{config.LIVE_FEED_JSON}")

    except Exception as e:
        print(e)

def on_error(wsapp, error):
    logger.error(f"---------Connection Error {error}-----------")

def on_close(wsapp):
    logger.info("---------Connection Close-----------")

def close_connection(sws):
    sws.MAX_RETRY_ATTEMPT = 0
    sws.close_connection()

def subscribeSymbol(token_list,sws):
    logger.info(f'Subscribe -------  {token_list}')
    sws.subscribe(config.CORRELATION_ID, config.FEED_MODE, token_list)

def connectFeed(sws,tokeList =None):
    
    
    def on_open(wsapp):
        logger.info("on open")
        token_list = [
            {
                "exchangeType": 1,
                "tokens": ["26009"]
            }
        ]
        if tokeList  : token_list.append(tokeList)
        sws.subscribe(config.CORRELATION_ID, config.FEED_MODE, token_list)

    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close
    threading.Thread(target =sws.connect,daemon=True).start()




if __name__ == "__main__":
    config.SMART_API_OBJ , config.SMART_WEB =  login()

    connectFeed(config.SMART_WEB)
    time.sleep(5)
    logger.info("-----------Subscribe--------")
    subscribeList  = [{"exchangeType": 2, "tokens": ["41734" ,"41735"]} , {"exchangeType": 5, "tokens": ["252453","250060"]}]
    subscribeSymbol(subscribeList,config.SMART_WEB)
    time.sleep(5)


    close_connection(config.SMART_WEB)
    logger.info("Connection closed")
    time.sleep(5)

    logger.info("-----------Exit--------")




"""
{'subscription_mode': 3, 'exchange_type': 2, 'token': '49697', 'sequence_number': 31482369, 
'exchange_timestamp': 1673337615000, 
'last_traded_price': 16030, 'subscription_mode_val': 'SNAP_QUOTE', 'last_traded_quantity': 50, 
'average_traded_price': 19249, 'volume_trade_for_the_day': 9622600, 
'total_buy_quantity': 145350.0, 'total_sell_quantity': 206000.0, 'open_price_of_the_day': 25090, 
'high_price_of_the_day': 32360, 'low_price_of_the_day': 14535, 
'closed_price': 32125, 'last_traded_timestamp': 1673337615, 'open_interest': 1362050, 
'open_interest_change_percentage': 4612141548726607190, 
'upper_circuit_limit': 95080, 'lower_circuit_limit': 5, '52_week_high_price': 54635, 
'52_week_low_price': 0, 
'best_5_buy_data': [{'flag': 0, 'quantity': 250, 'price': 16030, 'no of orders': 1},
 {'flag': 0, 'quantity': 500, 'price': 16035, 'no of orders': 2},
 {'flag': 0, 'quantity': 1650, 'price': 16040, 'no of orders': 7}, 
 {'flag': 0, 'quantity': 950, 'price': 16045, 'no of orders': 4}, {'flag': 
0, 'quantity': 850, 'price': 16050, 'no of orders': 5}], 
'best_5_sell_data': [{'flag': 1, 'quantity': 200, 'price': 15995, 'no of orders': 1},
 {'flag': 1, 'quantity': 650, 'price': 15990, 'no of orders': 5},
 {'flag': 1, 'quantity': 450, 'price': 15985, 'no of orders': 3}, 
 {'flag': 1, 'quantity': 700, 'price': 15980, 'no of orders': 2},
  {'flag': 1, 'quantity': 1400, 'price': 15975, 'no of orders': 7}]}


"""



"""
{'subscription_mode': 3, 'exchange_type': 2, 'token': '41735', 'sequence_number': 12989812, 'exchange_timestamp': 1689225333000, 'last_traded_price': 18570, 'subscription_mode_val': 'SNAP_QUOTE', 'last_traded_quantity': 25, 'average_traded_price': 21908, 'volume_trade_for_the_day': 22401150, 'total_buy_quantity': 1592025.0, 'total_sell_quantity': 480800.0, 'open_price_of_the_day': 30000, 'high_price_of_the_day': 34475, 'low_price_of_the_day': 16830, 'closed_price': 40440, 'last_traded_timestamp': 1689225333, 'open_interest': 2246775, 'open_interest_change_percentage': 4610956350471126153, 'upper_circuit_limit': 204385, 'lower_circuit_limit': 5, '52_week_high_price': 115845, '52_week_low_price': 0, 'best_5_buy_data': [{'flag': 1, 'quantity': 75, 'price': 18535, 'no of orders': 2}, {'flag': 1, 'quantity': 100, 'price': 18530, 'no of orders': 2}, {'flag': 1, 
'quantity': 500, 'price': 18525, 'no of orders': 4}, {'flag': 1, 'quantity': 725, 'price': 18520, 'no of orders': 9}, {'flag': 1, 'quantity': 125, 'price': 18515, 'no of orders': 2}], 'best_5_sell_data': [{'flag': 0, 'quantity': 150, 'price': 18575, 
'no of orders': 4}, {'flag': 0, 'quantity': 275, 'price': 18580, 'no of orders': 5}, {'flag': 0, 'quantity': 275, 'price': 18585, 'no of orders': 5}, {'flag': 0, 'quantity': 1025, 'price': 18590, 'no of orders': 3}, {'flag': 0, 'quantity': 200, 'price': 18595, 'no of orders': 5}]}

"""







































