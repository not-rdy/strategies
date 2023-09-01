from datetime import timedelta

from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now

TOKEN = 't.qAA92zgThHLAO6mNv_m9iydwxW1Na-gARgXdbsTnGfoOQmpXRT0YDrwIP4OOR8WCVPgPPJJ6Wh2e2goa_lQb7g'  # noqa: E501


def main():
    with Client(TOKEN) as client:
        for candle in client.get_all_candles(
            figi="FUTSI0923000",
            from_=now() - timedelta(minutes=100),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            print(candle)

    return 0


if __name__ == "__main__":
    main()
