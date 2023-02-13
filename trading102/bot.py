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

most_recent_tick = {}

async def receive_message(websocket):
    global most_recent_tick
    while True:
        message = await websocket.recv()
        data = json.loads(message)
        price = float(data["c"])
        timestamp = datetime.fromtimestamp(data["E"]/1000)
        change = 0
        if most_recent_tick:
            previous_timestamp = most_recent_tick["timestamp"]
            previous_price = most_recent_tick["price"]
            time_difference = (timestamp - previous_timestamp).total_seconds() / 60
            if time_difference >= 1: # 1 minute
                change = (price - previous_price) / previous_price * 100
                change = round(change, 2)
                print("Timestamp:", timestamp.strftime('%Y-%m-%d %H:%M:%S'), "Price:", price, "Change:", change, "%")
        most_recent_tick = {"timestamp": timestamp, "price": price}

async def run_websocket():
    async with websockets.connect("wss://stream.binance.com:9443/ws/btcusdt@ticker") as websocket:
        await receive_message(websocket)

asyncio.run(run_websocket())




