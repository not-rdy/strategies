import pandas as pd
from datetime import datetime
from tinkoff.invest import Client, CandleInterval


def get_init_historic_candles(
        token: str, figi: str,
        interval: CandleInterval,
        from_: datetime, to_: datetime) -> list:
    candles_list = []
    with Client(token) as client:
        for candle in client.get_all_candles(
            figi=figi,
            from_=from_, to=to_,
            interval=interval
        ):
            candles_list.append(candle)
    return candles_list


def get_init_df_candles(candles: list) -> pd.DataFrame:
    df_rows = []
    for candle in candles:
        df_rows.append(
            {
                'o': candle.open.units + float('.' + str(candle.open.nano)),  # noqa: E501
                'h': candle.high.units + float('.' + str(candle.high.nano)),  # noqa: E501
                'l': candle.low.units + float('.' + str(candle.low.nano)),  # noqa: E501
                'c': candle.close.units + float('.' + str(candle.close.nano)),  # noqa: E501
                'vol': candle.volume,
                'ts': candle.time
            }
        )
    df = pd.DataFrame(df_rows)
    df = df.sort_values(by='ts')
    return df
