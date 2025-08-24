from shared.data_manager import PriceDataManager


def handle_tick(data, **kwargs):
    price_manager: PriceDataManager = kwargs["manager"]
    new_candle_data = {}

    new_candle_data["close"] = data["tick"]["bid"]
    new_candle_data["epoch"] = data["tick"]["epoch"]
    price_manager.add_new_candle(new_candle_data)
