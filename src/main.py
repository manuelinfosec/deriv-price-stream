import asyncio
import os

import dotenv
from ws.client import TradingWebsocketClient
from shared.data_manager import PriceDataManager

dotenv.load_dotenv()

APP_ID = os.environ["APP_ID"]
DERIV_URL = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"


async def main():

    print(DERIV_URL)
    price_manager = PriceDataManager()
    client = TradingWebsocketClient(DERIV_URL, price_manager)
    await client.connect()

    print("Fetching historical candle data...")

    historical_data = await client.tick_history({
        "ticks_history": "BOOM1000",
        "adjust_start_time": 1,
        "granularity": 60,  # 1-minute timeframe
        "count": 300,
        "end": "latest",
        "start": 1, 
        "style": "candles",
    })
    price_manager.initialize_history(historical_data.get('candles', []))
    
    df = price_manager.get_dataframe()
    await client.stream_tick("BOOM1000")

    print(df)

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

