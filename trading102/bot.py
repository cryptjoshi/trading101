# import pandas as pd
# import numpy as np
# from binance.client import Client
# from utils import readConfig,green,red

# client = Client(readConfig['api_Key'], readConfig['api_secret'], testnet=True)
import asyncio
import websockets
import json
import pandas as pd
from datetime import datetime, timedelta

async def receive_message(websocket):
    most_recent_tick = None
    buy_price = None
    sell_price = None
    cumulative_change = 0
    while True:
        message = await websocket.recv()
        data = json.loads(message)
        price = float(data["c"])
        timestamp = datetime.fromtimestamp(data["E"]/1000)
        cumulative_change = 0
        print("Timestamp:", timestamp.strftime('%Y-%m-%d %H:%M:%S'), "Price:", price)
        if most_recent_tick:
            previous_timestamp = most_recent_tick["timestamp"]
            previous_price = most_recent_tick["price"]
            time_difference = (timestamp - previous_timestamp).total_seconds() / 60
            change = (price - previous_price) / previous_price * 100
            cumulative_change += change
            cumulative_change = round(cumulative_change, 2)
            if time_difference >= 1: # 1 minute
                cumulative_change = change
                print(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')} - Reset cumulative_change after 1 minute")
            
            if cumulative_change < -0.5 and not buy_price:
                buy_price = previous_price
                print(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')} - Buy price:{buy_price}")
            
            if cumulative_change >= 0.2 and buy_price is not None:
                sell_price = previous_price
                profit = sell_price - buy_price
                print(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')} - Sell price:{sell_price} - Profit:{profit}")
                buy_price =None
                sell_price=None
                cumulative_change = 0
                start_time = timestamp
            
            if (timestamp - start_time).total_seconds() >= 60:
                cumulative_change = 0.0
                start_time = timestamp
                print(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')} - Reset cumulative_change after 1 minute")
                


            print("Timestamp:", timestamp.strftime('%Y-%m-%d %H:%M:%S'), "Change:", change, "%", "Cumulative Change:", cumulative_change, "%")
      
        most_recent_tick = {"timestamp": timestamp, "price": price}

async def run_websocket():
    async with websockets.connect("wss://stream.binance.com:9443/ws/btcusdt@ticker") as websocket:
        await receive_message(websocket)

asyncio.run(run_websocket())




