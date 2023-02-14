import pandas as pd
import numpy as np
import pandas_ta as ta
import os,datetime,time
import websocket
import json


from binance.client import Client
from utils import readConfig,green,red

config = readConfig(r'Config.txt')
api_key = str(config['api_key_test'])
api_secret = str(config['api_secret_test'])
#print(api_key,api_secret)
client = Client(api_key,api_secret,testnet=True)
# info = Client.get_account()
entry = 25  #rsi entry
exit = 74   #rsi exit
df = pd.DataFrame()
testnetwork = 'wss://testnet.binance.vision/ws'
endpoint = 'wss://stream.binance.com:9443/ws'
our_msg = json.dumps({'method':'SUBSCRIBE',
                     'params':['btcusdt@ticker'],'id':1})

green('---------------------------------------------------')
green('           Trading101 V.1 by Jackyun')
green('---------------------------------------------------')

green('------------------- BALANCE -----------------------')
balance = client.get_asset_balance(asset='BTC')
print('Asset:' + balance['asset'])
print('Balance:' + balance['free'])
green('---------------------------------------------------')

def fetch_klines(asset):
    # fetch 1 minute klines for the last day up until now
    klines = client.get_historical_klines(asset, 
        Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")

    klines = [ [x[0],float(x[4])] for x in klines ]
    klines = pd.DataFrame(klines, columns = ["time","price"])
    klines["time"] = pd.to_datetime(klines["time"], unit = "ms")
    return klines


def sma50100(asset):
    df = fetch_klines(asset)
    df['SMA_50'] = df.price.rolling(50).mean()
    df['SMA_100'] = df.price.rolling(100).mean()
    df.dropna(inplace=True)
    df['condition'] = (df.SMA_50 > df.SMA_100)
    return df

def get_rsi(asset):
    klines = fetch_klines(asset)
    klines["rsi"]=ta.rsi(close=klines["price"], length = 14)

    return klines["rsi"].iloc[-1]

def log(msg):
    print(f"LOG: {msg}")
    if not os.path.isdir("logs"):
        os.mkdir("logs")

    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    with open(f"logs/{today}.txt", "a+") as log_file:
        log_file.write(f"{time} : {msg}\n")

def trade_log(sym, side, price, amount):
    log(f"{side} {amount} {sym} for {price} per")
    if not os.path.isdir("trades"):
        os.mkdir("trades")

    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")


    if not os.path.isfile(f"trades/{today}.csv"):
        with open(f"trades/{today}.csv", "w") as trade_file:
            trade_file.write("sym,side,amount,price\n")

    with open(f"trades/{today}.csv", "a+") as trade_file:
        trade_file.write(f"{sym},{side},{amount},{price}\n")
        
def create_account():

    account = {
            "is_buying":True,
            "assets":{},
            }

    with open("bot_account.json", "w") as f:
        f.write(json.dumps(account))

def is_buying():
    if os.path.isfile("bot_account.json"):

        with open("bot_account.json") as f:
            account = json.load(f)
            if "is_buying" in account:
                return account["is_buying"]
            else:
                return True

    else:
        create_account()
        return True
    
def do_trade(account,client, asset, side, quantity):

    if side == "buy":
        order = client.order_market_buy(
            symbol=asset,
            quantity=quantity)

        account["is_buying"] = False

    else:
        order = client.order_market_sell(
            symbol=asset,
            quantity=quantity)

        account["is_buying"] = True

    order_id = order["orderId"]

    while order["status"] != "FILLED":

        order = client.get_order(
            symbol=asset,
            orderId=order_id)

        time.sleep(1)

    price_paid = sum([ float(fill["price"]) * float(fill["qty"]) \
            for fill in order["fills"]])

    trade_log(asset, side, price_paid, quantity)

    with open("bot_account.json","w") as f:
        f.write(json.dumps(account))




asset = "BTCUSDT"    
rsi = get_rsi(asset)
old_rsi = rsi


while True:

    try:
        if not os.path.exists("bot_account.json"):
            create_account()

        with open("bot_account.json") as f:
            account = json.load(f)


        old_rsi = rsi
        rsi = get_rsi(asset)
        # sma = sma50100(asset)
        # print(sma)
        if account["is_buying"]:

            if rsi < entry and old_rsi > entry:
               do_trade(account, client, asset, "buy", 0.01)

        else:

            if rsi > exit and old_rsi < exit:
               do_trade(account, client, asset, "sell", 0.01)
        
        #print(rsi)
        time.sleep(10)

    except Exception as e:
        log("ERROR: " + str(e))