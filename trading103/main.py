import pandas as pd
import numpy as np
import websocket
import json

from binance.client import Client
from utils import readConfig,green,red

config = readConfig(r'Config.txt')
api_key = str(config['api_key_test'])
api_secret = str(config['api_secret_test'])
#print(api_key,api_secret)
Client = Client(api_key,api_secret,testnet=True)
# info = Client.get_account()
df = pd.DataFrame()
in_position = False
buydates,selldates = [],[]
buyorders,sellorders = [],[]

testnetwork = 'wss://testnet.binance.vision/ws'
endpoint = 'wss://stream.binance.com:9443/ws'
our_msg = json.dumps({'method':'SUBSCRIBE',
                     'params':['btcusdt@ticker'],'id':1})

green('---------------------------------------------------')
green('           Fibonanci V.1 by Jackyun')
green('---------------------------------------------------')

green('------------------- BALANCE -----------------------')
balance = Client.get_asset_balance(asset='BTC')
print('Asset:' + balance['asset'])
print('Balance:' + balance['free'])
green('---------------------------------------------------')


def getdata(symbol,start):
    frame  = pd.DataFrame(Client.get_historical_klines(symbol,'1h',start))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time','Open','High','Low','Close','Volume']
    frame.set_index('Time',inplace=True)
    frame.index = pd.to_datetime(frame.index,unit='ms')
    frame = frame.astype(float)
    
    return frame

def get_levels(date):
    values = [-0.618,0.618,1.618]
    series_ = df.loc[date:][1:2].squeeze()
    diff_ = series_.High - series_.Low
    lelvels = [series_.Low + i * diff_ for i in values]
    return lelvels
    
date = '2020-01-01'

df = getdata('BTCUSDT',date)
df = df.loc[date:][:25]
df['price'] = df.Open.shift(-1)
dates = np.unique(df.index.date)
buys,sells = [],[]
trade_dates = []
in_position = False

#print(df.index.date)

for date in dates:
    for index,row in df[date:][2:].iterrows():
        if not in_position:
            sl,entry,tp = get_levels(date)
            # print([sl,entry,tp])
            # print(row.Close,entry)
            if row.Close >= entry:
                buys.append(row.price)
                trade_dates.append(date)
                in_position = True
        if in_position:
            if row.Close >= tp or row.Close <= sl:
                sells.append(row.price)
                in_position = False
                break
trades = pd.DataFrame([buys,sells])
trades.columns = trade_dates
trades.index = ['Buy','Sell']
trades = trades.T
trades['PnL'] = trades.Sell - trades.Buy
trades['PnL_rel'] = trades.PnL/trades.Buy

print((trades.PnL_rel+1).cumprod())



 
