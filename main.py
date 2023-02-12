import pandas as pd
import numpy as np
from binance.client import Client
from utils import readConfig,green,red

Client = Client()

def getdata(symbol,start,config):
    api_key = str(config['api_key'])
    api_secret = str(config['api_secret'])
    frame  = pd.DataFrame(Client.get_historical_klines(symbol,'4h',start))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time','Open','High','Low','Close','Volume']
    frame.set_index('Time',inplace=True)
    frame = frame.astype(float)
    
    return frame



def main():
    green('---------------------')
    green('Trading101 V.1 by Jackyun')
    green('---------------------')
    config = readConfig(r'Config.txt')
    df = getdata('BTCUSDT','2021-01-01',config)
    df['SMA_50'] = df.Close.rolling(50).mean()
    df['SMA_100'] = df.Close.rolling(100).mean()
    df.dropna(inplace=True)
    df['condition'] = (df.SMA_50 > df.SMA_100)
    df['BUY'] =(df.condition) & (df.condition.shift(1)== False)
    df['shifted_open'] = df.Open.shift(-1)
    sl_range = 1 - np.arange(0.01,0.05,0.01)
    tp_range = 1 + np.arange(0.01,0.05,0.01)      
    
    train_ = df[:int(len(df)*0.7)]
    test_ = df[int(len(df)*0.7):]
    
    for sl in sl_range:
        for tp in tp_range:
            print('stop loss:' + str(sl), 'target profit:'+ str(tp))
            strat_loop(train_,sl,tp)
    
    strat_loop(test_,0.96,1.01)
 
    
    
def strat_loop(data,sl,tp):
    in_position = False
    
    buydates,selldates = [],[]
    buyprices,sellprices = [],[]
    
    for index,row in data.iterrows():
        if not in_position and row.BUY == True:
            buyprice = row.shifted_open
            buydates.append(index)
            buyprices.append(buyprice)
            in_position = True
        if in_position:
            if row.Low < buyprice * sl:
                sellprice = buyprice *sl
                sellprices.append(sellprice)
                selldates.append(index)
                in_position = False
            elif row.High > buyprice * tp:
                sellprice = buyprice * tp
                sellprices.append(sellprice)
                selldates.append(index)
                in_position = False
    
    profits = pd.Series([(sell-buy)/buy -  0.0015 for sell,buy in zip(sellprices,buyprices)])
    
    print((profits+1).prod())
            
    
    
            
            
    
    
    #df['SMA_50']
  
    #trading = Trading(config) #{'User':'Master','token':'xxxxxxxxxx','api_key':'yyyyyyyyyyy','api_secret':'zzzzzzzzzzz'})
    
if __name__ == '__main__':
    main()