import os
import asyncio

from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction
)
from data_updater import DataUpdater
from signal_maker import SignalMaker
from account_manager import ACCManager
from config import params


async def request_iterator():
    yield MarketDataRequest(
        subscribe_candles_request=SubscribeCandlesRequest(
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,  # noqa: E501
            instruments=[
                CandleInstrument(
                    figi=params['figi'],
                    interval=params['candles_interval']
                )
            ],
        )
    )
    while True:
        await asyncio.sleep(1)


async def main():

    du = DataUpdater(
        TOKEN=os.getenv('TOKEN'),
        figi=params['figi'],
        candles_interval=params['candles_interval'],
        init_candles_depth=params['init_candles_depth'])
    sm = SignalMaker(
        params['ma_window_width'],
        params['q_std_rolling_width'],
        params['coeff_for_SL'],
        params['q'],
        params['q_window_width'])
    am = ACCManager(
        token=os.getenv('TOKEN'),
        figi=params['figi'],
        id_acc=os.getenv('ACCOUNT'))

    async with AsyncClient(os.getenv('TOKEN')) as client:
        async for candle_tick in client.market_data_stream.market_data_stream(
            request_iterator()
        ):

            if candle_tick.candle is not None:

                df_candles_periodic = du.update(candle_tick)

                signal = sm.get_signal(
                    candles=df_candles_periodic, candle_tick=candle_tick)  # noqa: E501
                if signal is not None:
                    print(signal)

                am.manage_orders_and_sl(
                    signal=signal, quantity=params['quantity'])


if __name__ == "__main__":
    asyncio.run(main())
