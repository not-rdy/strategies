import time

from tinkoff.invest import (
    CandleInstrument,
    Client,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
)

TOKEN = 't.qAA92zgThHLAO6mNv_m9iydwxW1Na-gARgXdbsTnGfoOQmpXRT0YDrwIP4OOR8WCVPgPPJJ6Wh2e2goa_lQb7g'  # noqa: E501


def main():
    def request_iterator():
        yield MarketDataRequest(
            subscribe_candles_request=SubscribeCandlesRequest(
                waiting_close=True,
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,  # noqa: E501
                instruments=[
                    CandleInstrument(
                        figi="FUTSI0923000",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,  # noqa: E501
                    )
                ],
            )
        )
        while True:
            time.sleep(1)

    with Client(TOKEN) as client:
        for marketdata in client.market_data_stream.market_data_stream(
            request_iterator()
        ):
            print(f"\n{marketdata}")


if __name__ == "__main__":
    main()
