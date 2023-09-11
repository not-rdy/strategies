from typing import Union
from pandas import DataFrame
from tinkoff.invest import MarketDataResponse


class SignalMaker:

    def __init__(
            self,
            ma_window_width: int,
            q_std_rolling_width: int,
            # sigma_coeff_for_SL: 0.1,
            coeff_for_SL: 0.05,
            q: float,
            q_window_width: int):

        self.ma_window_width = ma_window_width
        self.q_window_width = q_window_width
        self.q_std_rolling_width = q_std_rolling_width
        self.q = q
        self.coeff_sl = coeff_for_SL

        self.ma_current = None
        self.high_q_current = None
        self.low_q_current = None
        self.high_q_std_current = None
        self.low_q_std_current = None
        self.sl = None

        self.locked = False
        self.side = None

    def __calc_attr(self, candles: DataFrame) -> None:

        if candles is not None:

            candles['ma'] = candles['close'].rolling(self.ma_window_width).mean()  # noqa: E501
            candles['high_q'] = candles['ma'] + (candles['high'] - candles['ma'])\
                .rolling(self.q_window_width).quantile(self.q)  # noqa: E501
            candles['low_q'] = candles['ma'] - (candles['ma'] - candles['low'])\
                .rolling(self.q_window_width).quantile(self.q)  # noqa: E501
            candles['low_q_std'] = candles['low_q'].rolling(self.q_std_rolling_width).std()  # noqa: E501
            candles['high_q_std'] = candles['high_q'].rolling(self.q_std_rolling_width).std()  # noqa: E501

            self.ma_current = candles['close'].iloc[-self.ma_window_width:].mean()  # noqa: E501
            self.high_q_current = self.ma_current + (candles['high'] - candles['ma'])\
                .iloc[-self.q_window_width:].quantile(self.q)  # noqa: E501
            self.low_q_current = self.ma_current - (candles['ma'] - candles['low'])\
                .iloc[-self.q_window_width:].quantile(self.q)  # noqa: E501
            self.low_q_std_current = candles['low_q'].iloc[-self.q_std_rolling_width:].std()  # noqa: E501
            self.high_q_std_current = candles['high_q'].iloc[-self.q_std_rolling_width:].std()  # noqa: E501

    @staticmethod
    def __calc_price(candle_tick: MarketDataResponse) -> float:
        price = candle_tick.candle.close.units\
            + float('.' + str(candle_tick.candle.close.nano))
        return price

    def get_signal(
            self,
            candles: DataFrame,
            candle_tick: MarketDataResponse) -> Union[dict, None]:

        self.__calc_attr(candles)
        price = self.__calc_price(candle_tick)

        if self.ma_current is None:
            return None

        if not self.locked and price <= self.low_q_current:
            self.side = 'long'
            self.locked = True
            # self.sl = self.low_q_current - self.low_q_std_current * self.sigma_coeff  # noqa: E501
            self.sl = self.low_q_current - price * self.coeff_sl
            return {
                'action': 'open', 'side': self.side,
                'price': price, 'sl': self.sl
                }
        if not self.locked and price >= self.high_q_current:
            self.side = 'short'
            self.locked = True
            # self.sl = self.high_q_current + self.high_q_std_current * self.sigma_coeff  # noqa: E501
            self.sl = self.high_q_current + price * self.coeff_sl
            return {
                'action': 'open', 'side': self.side,
                'price': price, 'sl': self.sl
                }
        if self.locked and self.side == 'long'\
                and (price >= self.ma_current or price <= self.sl):
            self.locked = False
            return {
                'action': 'close', 'side': self.side, 'price': price,
                }
        if self.locked and self.side == 'short'\
                and (price <= self.ma_current or price >= self.sl):
            self.locked = False
            return {
                'action': 'close', 'side': self.side, 'price': price,
                }
