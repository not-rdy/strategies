import os
import time
from tinkoff.invest import (
    CandleInstrument,
    Client,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval
)
from sequence_maker import SequenceMaker
from signal_maker import SignalMaker
from account_manager import AccountManager
from datetime import datetime
from tinkoff.invest import CandleInterval

figi = 'BBG004730N88'
interval = CandleInterval.CANDLE_INTERVAL_5_MIN
subscription_interval = SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES
seq_window = 5
quantity = 2

seq = SequenceMaker(
    figi=figi,
    interval=interval,
    seq_window=5)

sig = SignalMaker()
sig.fit(
    figi=figi,
    interval=interval,
    from_=datetime(year=2021, month=12, day=31),
    to_=datetime.now(),
    probas_threshold=0.55,
    seq_window=seq_window
)

acm = AccountManager(
    figi=figi,
    id_acc=os.getenv('ACCOUNT'))


def request_iterator():
    yield MarketDataRequest(
        subscribe_candles_request=SubscribeCandlesRequest(
            waiting_close=True,
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,  # noqa: E501
            instruments=[
                CandleInstrument(
                    figi=figi,
                    interval=subscription_interval,
                )
            ],
        )
    )
    while True:
        time.sleep(1)


with Client(os.getenv('TOKEN')) as client:
    for marketdata in client.market_data_stream.market_data_stream(
        request_iterator()
    ):
        sequence = seq.make(marketdata)
        signal = sig.make(sequence)
        print(f'\nSignal: {signal}')
        acm.manage_orders(signal=signal, quantity=quantity)
