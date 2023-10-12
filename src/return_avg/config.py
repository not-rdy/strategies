from tinkoff.invest import SubscriptionInterval

params = {

    'quantity': 1,
    'figi': "BBG004730N88",
    'candles_interval': SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,

    # DataUpdater
    'init_candles_depth': 100,

    # SignalMaker
    'ma_window_width': 5,
    'q_std_rolling_width': 20,
    'coeff_for_SL': 0.01,
    'q': 0.8,
    'q_window_width': 20
}
