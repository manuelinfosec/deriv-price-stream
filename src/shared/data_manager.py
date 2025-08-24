import pandas as pd
from typing import Dict, List
import pandas_ta as ta


class PriceDataManager:
    """
    Manages a time-series of price candles using a pandas DataFrame
    """

    def __init__(self):
        # Initialize an empty DataFrame with the expected structure
        self.candles_df = pd.DataFrame(
            columns=["epoch", "open", "high", "low", "close", "rsi", "macd", "rsi", "macd"]
        )
        print("\n📊 PriceDataManager initialized to use pandas DataFrame")

    def initialize_history(self, historical_candles: List[Dict]):
        """
        Populates the DataFrame with a list of historical candle data.
        """
        if not historical_candles:
            return

        # Convert the list of dictionaries directly into a DataFrame
        history_df = pd.DataFrame(historical_candles)

        # Ensure the 'epoch' column is treated as a date type
        history_df["epoch"] = pd.to_datetime(history_df["epoch"], unit="s")
        # history_df = history_df.sort_values(by="epoch")

        ta_macd = ta.macd(
                history_df["close"], fast=12, slow=26, signal=9
        )

        if ta_macd is not None:
            history_df["macd"] = ta_macd["MACD_12_26_9"]


        history_df["rsi"] = ta.rsi(history_df["close"], length=6)

        # return only time and close
        self.candles_df = history_df.loc[:, ["epoch", "close", "rsi", "macd"]]

        print(
            f"\n📈 DataFrame initialized with {len(self.candles_df)} historical candles."
        )

    def add_new_candle(self, new_candle: Dict):
        """Append a new live candle to the DataFrame"""
        # Convert the new candle dictionary to a DataFrame with one row
        new_row_df = pd.DataFrame([new_candle])

        new_row_df["epoch"] = pd.to_datetime(new_row_df["epoch"], unit="s")

        # Cancatenate the new row to the main DataFrame
        self.candles_df = pd.concat([self.candles_df, new_row_df], ignore_index=True)

        ta_macd = ta.macd(
                self.candles_df["close"], fast=12, slow=26, signal=9
        )

        if ta_macd is not None:
            self.candles_df["macd"] = ta_macd["MACD_12_26_9"]


        self.candles_df["rsi"] = ta.rsi(self.candles_df["close"], length=6)

        # Optional: Trim the DataFrame to a max length to prevent memory issues
        max_length = 1000
        if len(self.candles_df) > max_length:
            print("\n✂️ About to trim Price DataFrame")
            self.candles_df = self.candles_df.iloc[-max_length:]

        print("🕯️ New candle added.")
        last_row = self.candles_df.iloc[-1]
        print(last_row)

    def get_dataframe(self):
        """
        Returns the current, complete DataFrame of all candles.
        """
        return self.candles_df
