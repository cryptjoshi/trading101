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
    green('Pynance V.1 by CJ')
    green('---------------------')
    config = readConfig(r'Config.txt')
    df = getdata('BTCUSDT','2021-01-01',config)
    #df['SMA_50']
    print(df)
    #trading = Trading(config) #{'User':'Master','token':'xxxxxxxxxx','api_key':'yyyyyyyyyyy','api_secret':'zzzzzzzzzzz'})
    
if __name__ == '__main__':
    main()