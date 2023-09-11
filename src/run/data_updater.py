import pandas as pd
from datetime import timedelta
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now


class DataUpdater:

    def __init__(
            self,
            TOKEN: str, figi: str,
            candles_interval: CandleInterval, init_candles_depth: int) -> None:

        """
        candles interval: 1min, 5min, 15min
        """

        self.token = TOKEN
        self.figi = figi
        self.interval = candles_interval
        self.depth = init_candles_depth
        self.last_candle = None
        self.blast_stream_candle = None
        self.last_stream_candle = None
        self.df_candles = self.__get_init_df_candles(self.__get_init_historic_candles())  # noqa: E501

    def __get_init_historic_candles(self) -> list:
        candles_list = []
        with Client(self.token) as client:
            for candle in client.get_all_candles(
                figi=self.figi,
                from_=now() - timedelta(minutes=self.depth),
                interval=self.interval
            ):
                candles_list.append(candle)
        return candles_list

    def __get_init_df_candles(self, candles: list) -> pd.DataFrame:
        df_rows = []
        for candle in candles:
            df_rows.append(
                {
                    'open': candle.open.units + float('.' + str(candle.open.nano)),  # noqa: E501
                    'high': candle.high.units + float('.' + str(candle.high.nano)),  # noqa: E501
                    'low': candle.low.units + float('.' + str(candle.low.nano)),  # noqa: E501
                    'close': candle.close.units + float('.' + str(candle.close.nano)),  # noqa: E501
                    'volume': candle.volume,
                    'time': candle.time
                }
            )
        self.last_candle = candles[-1]
        return pd.DataFrame(df_rows)

    def update(self, candle) -> None:
        self.blast_stream_candle = self.last_stream_candle
        self.last_stream_candle = candle.candle

        if self.blast_stream_candle is None or self.last_stream_candle is None:
            return None

        if self.blast_stream_candle.open.units != self.last_stream_candle.open.units\
                or self.blast_stream_candle.open.nano != self.last_stream_candle.open.nano:  # noqa: E501
            new_candle = pd.DataFrame(
                {
                    'open': self.blast_stream_candle.open.units + float('.' + str(self.blast_stream_candle.open.nano)),  # noqa: E501
                    'high': self.blast_stream_candle.high.units + float('.' + str(self.blast_stream_candle.high.nano)),  # noqa: E501
                    'low': self.blast_stream_candle.low.units + float('.' + str(self.blast_stream_candle.low.nano)),  # noqa: E501
                    'close': self.blast_stream_candle.close.units + float('.' + str(self.blast_stream_candle.close.nano)),  # noqa: E501
                    'volume': self.blast_stream_candle.volume,
                    'time': self.blast_stream_candle.time
                },
                index=[0]
            )
            self.df_candles = pd.concat([self.df_candles.iloc[1:], new_candle])
            return self.df_candles
        else:
            return None
