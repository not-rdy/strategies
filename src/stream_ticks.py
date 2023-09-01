import time
from tinkoff.invest import (
    Client,
    MarketDataRequest,
    SubscribeLastPriceRequest,
    SubscriptionAction,
    LastPriceInstrument
)

# не забыть скрыть в os.environ
# песочница
TOKEN = 't.qAA92zgThHLAO6mNv_m9iydwxW1Na-gARgXdbsTnGfoOQmpXRT0YDrwIP4OOR8WCVPgPPJJ6Wh2e2goa_lQb7g'  # noqa: E501


def main():
    def request_iterator():
        yield MarketDataRequest(
            subscribe_last_price_request=SubscribeLastPriceRequest(
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,  # noqa: E501
                instruments=[
                    LastPriceInstrument(figi='FUTSI0923000')
                    ]
            )
        )
        while True:
            time.sleep(1)

    with Client(TOKEN) as client:
        for lastprice in client.market_data_stream.market_data_stream(
            request_iterator()
        ):
            print(f"\n{lastprice}")


if __name__ == '__main__':
    main()
