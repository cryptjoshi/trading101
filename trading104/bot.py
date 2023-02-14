import asyncio
import websockets
import json
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
from binance.client import Client
from utils import readConfig,green,red
from datetime import datetime 

config = readConfig(r'Config.txt')
api_key = str(config['api_key_test'])
api_secret = str(config['api_secret_test'])
# Replace YOUR_API_KEY and YOUR_SECRET_KEY with your actual API keys
client = Client(api_key,api_secret,testnet=True)

# Replace "BTCUSDT" with the symbol you want to trade
symbol = "BTCUSDT"

# Replace "0.001" with the quantity you want to trade
quantity = "0.001"

# Replace "1" or "3" with your desired profit target
profit_target = 1  # or 3

# Replace "1" or "4" with your desired timeframe (in hours)
timeframe = 1  # or 4

# Define the period for the SMA and RSI indicators
sma_period = 20
rsi_period = 14

columns = ['timestamp', 'open', 'high', 'low', 'close']
df = pd.DataFrame(columns=columns)
df = None
async def receive_message(websocket):
    global df
    data = json.loads(await websocket.recv())
    close_price = float(data["c"])
    open_price = float(data['o'])
    high_price = float(data['h'])
    low_price = float(data['l'])
    timestamp = datetime.fromtimestamp(data["E"]/1000)
    # timestamp = data['k']['t'] / 1000
    # open_price = float(data['k']['o'])
    # high_price = float(data['k']['h'])
    # low_price = float(data['k']['l'])
    # close_price = float(data['k']['c'])
    #df = df.append({'timestamp': timestamp, 'open': open_price, 'high': high_price, 'low': low_price, 'close': close_price}, ignore_index=True)
    data = pd.DataFrame({'timestamp': timestamp, 'open': open_price, 'high': high_price, 'low': low_price, 'close': close_price},index=[pd.to_datetime(data['E'],unit='ms')])
    df = pd.concat([df,data],axis=0)
 
    # Calculate the SMA and RSI indicators
    # df['sma'] = ta.sma(df['close'], length=sma_period)
    # df['rsi'] = ta.rsi(df['close'], length=rsi_period)
    df['sma'] = df.close.rolling(sma_period).mean()
    df['rsi'] = ta.rsi(close=df["close"], length = rsi_period)
    #df['SMA_100'] = df.Close.rolling(100).mean()
    
    
    # heck if the current price is above the SMA and the RSI is below 30
    current_price = close_price
    if current_price > df['sma'].iloc[-1] and df['rsi'].iloc[-1] < 30:
        print(df)
    #     # Calculate the take profit and stop loss prices
    #     take_profit_price = str(round(current_price * (1 + profit_target/100), 2))
    #     stop_loss_price = str(round(current_price * 0.99, 2))
    #     #if account["is_buying"]:
    #         # Place the order
    #     order = client.create_order(
    #         symbol=symbol,
    #         side=Client.SIDE_BUY,
    #         type=Client.ORDER_TYPE_LIMIT,
    #         timeInForce=Client.TIME_IN_FORCE_GTC,
    #         quantity=quantity,
    #         price=current_price,
    #         stopPrice=stop_loss_price,
    #         icebergQty='0',
    #         newOrderRespType=Client.ORDER_RESP_TYPE_RESULT,
    #         recvWindow=10000
    #     )


    #     trade_log(symbol, Client.SIDE_BUY, take_profit_price, quantity)
    #     # Wait for the specified timeframe
    #     await asyncio.sleep(timeframe * 60 * 60)

    #     # Place the take profit order
    #     take_profit_order = client.create_order(
    #         symbol=symbol,
    #         side=Client.SIDE_SELL,
    #         type=Client.ORDER_TYPE_LIMIT,
    #         timeInForce=Client.TIME_IN_FORCE_GTC,
    #         quantity=quantity,
    #         price=take_profit_price,
    #         icebergQty='0',
    #         newOrderRespType=Client.ORDER_RESP_TYPE_RESULT,
    #         recvWindow=10000
    #     )
    #     trade_log(symbol, Client.SIDE_SELL, take_profit_price, quantity)


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

    # print("Timestamp:", timestamp.strftime('%Y-%m-%d %H:%M:%S'), "Price:", current_price)
    # print(df)
    
async def run_websocket():
    async with websockets.connect("wss://stream.binance.com:9443/ws/btcusdt@ticker") as websocket:
        while True:
            await receive_message(websocket)

asyncio.get_event_loop().run_until_complete(run_websocket())