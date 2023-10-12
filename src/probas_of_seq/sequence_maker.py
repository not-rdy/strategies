import os
from datetime import datetime, timedelta
from tinkoff.invest import CandleInterval, MarketDataResponse
from tinkoff.invest.utils import quotation_to_decimal
from utils import get_init_historic_candles, get_init_df_candles


class SequenceMaker:

    def __init__(
            self,
            figi: str, interval: CandleInterval, seq_window: int) -> None:
        self.figi = figi
        self.interval = interval
        if interval == CandleInterval.CANDLE_INTERVAL_1_MIN:
            self.timedelta_minutes = seq_window + 1
        elif interval == CandleInterval.CANDLE_INTERVAL_5_MIN:
            self.timedelta_minutes = (seq_window + 1) * 5
        elif interval == CandleInterval.CANDLE_INTERVAL_10_MIN:
            self.timedelta_minutes = (seq_window + 1) * 10
        else:
            self.timedelta_minutes = None

        self.last_price = None
        self.queue_labels = []
        self.__make_init_sequence()

    def __make_init_sequence(self) -> None:
        candles = get_init_historic_candles(
            token=os.getenv('TOKEN'),
            figi=self.figi,
            interval=self.interval,
            from_=datetime.now() - timedelta(minutes=self.timedelta_minutes),
            to_=datetime.now()
        )
        candles = get_init_df_candles(candles)
        self.last_price = candles.iloc[5]['c']
        self.queue_labels = candles.iloc[0:6]['c'].diff().dropna()\
            .map(lambda x: '1' if x > 0 else '0' if x == 0 else '-1').tolist()
        return None

    def make(self, marketdata: MarketDataResponse) -> str:
        if marketdata.ping is None and marketdata.candle is not None:
            current_price = quotation_to_decimal(marketdata.candle.close)
            self.queue_labels.pop(0)
            if current_price < self.last_price:
                self.queue_labels.append('-1')
            elif current_price > self.last_price:
                self.queue_labels.append('1')
            else:
                self.queue_labels.append('0')
            self.last_price = current_price
            return ''.join(self.queue_labels)
        else:
            return None
