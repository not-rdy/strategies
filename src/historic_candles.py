import os
from datetime import timedelta

from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now

TOKEN = os.getenv('TOKEN')
figi = 'FUTSI0923000'


def main():
    with Client(TOKEN) as client:
        for candle in client.get_all_candles(
            figi=figi,
            from_=now() - timedelta(minutes=100),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            print(candle)

    return 0


if __name__ == "__main__":
    main()
