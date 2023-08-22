import pandas as pd
from typing import Tuple, Union


class Signal:
    """
    flag states: 1 - buy (long), 0 - sell (short)
    locked states: 1 - locked, 0 - open
    """

    def __init__(self):
        self.locked = 0
        self.flag = None

    def __call__(self, open, high, low, ma, high_q, low_q) -> dict:
        # свободная сделка: покупка возле нижнего квантиля
        if self.locked == 0 and open > low_q and low <= low_q:
            self.flag = 1
            self.locked = 1
            return {'type': self.flag, 'price': low_q, 'action': 'open'}
        # свободная сделка: продажа возле верхнего квантиля
        elif self.locked == 0 and open < high_q and high >= high_q:
            self.flag = 0
            self.locked = 1
            return {'type': self.flag, 'price': high_q, 'action': 'open'}
        # сделка: покупка возле нижнего квантиля и продажа возле MA
        elif self.locked == 1 and self.flag == 1 and open < ma and high >= ma:
            self.flag = 0
            self.locked = 0
            return {'type': self.flag, 'price': ma, 'action': 'close'}
        # сделка: продажа возле верхнего квантиля и покупка возле MA
        elif self.locked == 1 and self.flag == 0 and open > ma and low <= ma:
            self.flag = 1
            self.locked = 0
            return {'type': self.flag, 'price': ma, 'action': 'close'}


class StopLoss:

    def __init__(self) -> None:
        self.stop_loss = None

    def __call__(self, last: pd.Series, sigma_coeff: int):
        if pd.isna(last['signal']):
            return self.stop_loss
        if last['signal']['action'] == 'open' and last['signal']['type'] == 1:
            self.stop_loss = last['low_q'] - last['low_q_std'] * sigma_coeff
            return self.stop_loss
        elif last['signal']['action'] == 'open' and last['signal']['type'] == 0:  # noqa: E501
            self.stop_loss = last['high_q'] + last['high_q_std'] * sigma_coeff
            return self.stop_loss
        elif last['signal']['action'] == 'close' and\
                (last['signal']['type'] == 0 or last['signal']['type'] == 1):
            return self.stop_loss


class IsReachedSL:

    def __init__(self):
        self.open = None
        self.type = None

    def __call__(self, row: pd.Series) -> bool:
        if not pd.isna(row['signal']) and row['signal']['action'] == 'open':
            self.open = True
            self.type = row['signal']['type']

        if self.open and self.type == 1:
            return row['Low'] <= row['sl']
        if self.open and self.type == 0:
            return row['High'] >= row['sl']

        if not pd.isna(row['signal']) and row['signal']['action'] == 'close':
            self.open = False


class GetProfit:

    def __init__(self):
        self.open = None
        self.type = None

    def __call__(self, row: pd.Series) -> float:
        if not pd.isna(row['signal']) and row['signal']['action'] == 'open':
            self.open = True
            self.type = row['signal']['type']

        # сделка открыта, на повышение, момент открытия сделки, sl не достигнут
        if self.open and self.type == 1 and not pd.isna(row['signal']) and\
                row['signal']['action'] == 'open' and not row['is_reached_sl']:
            return row['Close'] - row['signal']['price']
        # сделка открыта, на повышение, момент окрытия сделки, sl достигнут
        if self.open and self.type == 1 and not pd.isna(row['signal']) and\
                row['signal']['action'] == 'open' and row['is_reached_sl']:
            self.open = False
            self.type = None
            return row['sl'] - row['signal']['price']
        # сделка открыта, на повышение, после открытия сделки, sl не достигнут
        if self.open and self.type == 1 and\
                pd.isna(row['signal']) and not row['is_reached_sl']:
            return row['Close'] - row['Open']
        # сделка открыта, на повышение, после открытия сделки, sl достигнут
        if self.open and self.type == 1 and\
                pd.isna(row['signal']) and row['is_reached_sl']:
            self.open = False
            self.type = None
            return row['sl'] - row['Open']
        # сделка открыта, на повышение, момент закрытия сделки, sl не достигнут
        if self.open and self.type == 1 and not pd.isna(row['signal']) and\
                row['signal']['action'] == 'close' and not row['is_reached_sl']:  # noqa: E501
            self.open = False
            self.type = None
            return row['signal']['price'] - row['Open']
        # сделка открыта, на повышение, момент закрытия сделки, sl достигнут
        if self.open and self.type == 1 and not pd.isna(row['signal']) and\
                row['signal']['action'] == 'close' and row['is_reached_sl']:
            self.open = False
            self.type = None
            return row['sl'] - row['Open']

        # сделка открыта, на понижение, момент открытия сделки, sl не достигнут
        if self.open and self.type == 0 and not pd.isna(row['signal'])\
                and row['signal']['action'] == 'open' and not row['is_reached_sl']:  # noqa: E501
            return row['signal']['price'] - row['Close']
        # сделка открыта, на понижение, момент открытия сделки, sl достигнут
        if self.open and self.type == 0 and not pd.isna(row['signal'])\
                and row['signal']['action'] == 'open' and row['is_reached_sl']:
            self.open = False
            self.type = None
            return row['signal']['price'] - row['sl']
        # сделка открыта, на понижение, после открытия сделки, sl не достигнут
        if self.open and self.type == 0 and\
                pd.isna(row['signal']) and not row['is_reached_sl']:
            return row['Open'] - row['Close']
        # сделка открыта, на понижение, после открытия сделки, sl достигнут
        if self.open and self.type == 0 and\
                pd.isna(row['signal']) and row['is_reached_sl']:
            self.open = False
            self.type = None
            return row['Open'] - row['sl']
        # сделка открыта, на понижение, момент закрытия сделки, sl не достигнут
        if self.open and self.type == 0 and not pd.isna(row['signal']) and\
                row['signal']['action'] == 'close' and not row['is_reached_sl']:  # noqa: E501
            self.open = False
            self.type = None
            return row['Open'] - row['signal']['price']
        # сделка открыта, на понижение, момент закрытия сделки, sl достигнут
        if self.open and self.type == 0 and not pd.isna(row['signal']) and\
                row['signal']['action'] == 'close' and row['is_reached_sl']:
            self.open = False
            self.type = None
            return row['Open'] - row['sl']

        if not pd.isna(row['signal']) and row['signal']['action'] == 'close':
            self.open = False
            self.type = None


class TradingSystem:

    def __init__(
            self,
            ma_window_width: int,
            q_std_rolling_width: int,
            sigma_coeff_for_SL: float,
            q: float,
            q_window_width: int) -> None:

        self.ma_window_width = ma_window_width
        self.q_std_rolling_width = q_std_rolling_width
        self.sigma_coeff_for_SL = sigma_coeff_for_SL
        self.q = q
        self.q_window_width = q_window_width
        self.signal = Signal()
        self.stoploss = StopLoss()
        self.is_reached_sl = IsReachedSL()
        self.get_profit = GetProfit()

    def __get_prepared_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df.sort_values(by='Date')
        df['Date'] = pd.to_datetime(df['Date'] * 1e6)
        df = df.set_index('Date')
        return df

    def __get_attr(
            self,
            df: pd.DataFrame) -> Tuple[pd.Series]:
        df['ma'] = df['Close'].rolling(self.ma_window_width).mean()
        df['high_q'] = df['ma'] + (df['High'] - df['ma'])\
            .rolling(self.q_window_width).quantile(self.q)
        df['low_q'] = df['ma'] - (df['ma'] - df['Low'])\
            .rolling(self.q_window_width).quantile(self.q)
        df['low_q_std'] = df['low_q'].rolling(self.q_std_rolling_width).std()
        df['high_q_std'] = df['high_q'].rolling(self.q_std_rolling_width).std()
        return df

    def get_signal(self, df: pd.DataFrame) -> Union[dict, None]:
        df = df.copy()
        df = self.__get_prepared_data(df)
        df = self.__get_attr(df)
        self.last = df.iloc[-1].copy()
        self.last['signal'] = self.signal(
            self.last['Open'], self.last['High'], self.last['Low'],
            self.last['ma'], self.last['high_q'], self.last['low_q']
        )
        return self.last['signal']

    def get_stoploss(self) -> float:
        self.last['sl'] = self.stoploss(
            self.last, self.sigma_coeff_for_SL)
        return self.last['sl']

    def reached_sl(self) -> bool:
        self.last['is_reached_sl'] = self.is_reached_sl(
            self.last[['High', 'Low', 'signal', 'sl']]
            )
        return self.last['is_reached_sl']

    def profit(self) -> float:
        self.last['profit'] = self.get_profit(
            self.last[['Open', 'Close', 'signal', 'sl', 'is_reached_sl']]
        )
        return self.last['profit']
