import asyncio
import os

import dotenv
from ws.client import TradingWebsocketClient
from shared.data_manager import PriceDataManager

dotenv.load_dotenv()

APP_ID = os.environ["APP_ID"]
DERIV_URL = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"


async def main():
    price_manager = PriceDataManager()
    client = TradingWebsocketClient(DERIV_URL, price_manager)
    print(client)


if __name__ == "__main__":
    asyncio.run(main())
