import pandas as pd
import matplotlib.animation as animation
import mplfinance as mpf
from utils import MarkUp, StopLoss, IsReachedSL
from utils import get_attr, get_prepared_data, get_reached_sl_price


def animate(ival):

    data = df.iloc[ival:ival+params['fig_width']].copy()
    data = get_attr(
        data,
        params['ma_window_width'],
        params['q'],
        params['q_window_width'],
        params['q_std_rolling_length'])
    data['mark'] = data.apply(
        lambda x: markup(
            x['Open'], x['High'], x['Low'],
            x['ma'], x['high_q'], x['low_q']),
        axis=1
        )
    data['sl'] = data.apply(
        lambda x: stoploss(x, params['sigma_coeff_for_SL']), axis=1)
    data['is_reached_sl'] = data.apply(lambda x: is_reached_sl(x), axis=1)
    data['reached_sl_price'] = data[['sl', 'is_reached_sl']]\
        .apply(lambda x: get_reached_sl_price(x), axis=1)
    ax1.clear()
    x = range(0, params['fig_width'])
    mpf.plot(
        data[['Open', 'High', 'Low', 'Close', 'Volume']],
        ax=ax1, type='candle')
    ax1.plot(
        x, data['ma'],
        label='ma', color='black')
    ax1.plot(
        x, data['high_q'],
        label='high_q', color='green')
    ax1.plot(
        x, data['low_q'],
        label='low_q', color='red')
    ax1.scatter(
        x,
        data['mark'].map(lambda x: x['price'] if x is not None else None)
    )
    ax1.hlines(
        y=data['sl'].iloc[-1],
        xmin=0, xmax=params['fig_width'])
    ax1.scatter(
        x,
        data['reached_sl_price'])
    ax1.legend()


params = {
    'figsize': (15, 7),
    'fig_width': 100,
    'ma_window_width': 5,
    'q_std_rolling_length': 20,
    'sigma_coeff_for_SL': 2,
    'q': .8,
    'q_window_width': 20
}

markup = MarkUp()
stoploss = StopLoss()
is_reached_sl = IsReachedSL()

df = pd.read_csv(
    '/home/rustem/projs/strategies/data/raw/BTC-USDT.csv',
    index_col=0)[['ts', 'o', 'h', 'l', 'c', 'vol']].sort_values(by='ts')
df = get_prepared_data(df)

fig, ax = mpf.plot(
    df.iloc[0:params['fig_width']],
    type='candle',
    returnfig=True,
    figsize=params['figsize'])
ax1 = ax[0]

ani = animation.FuncAnimation(
    fig, animate, interval=500, save_count=100)
# ani.save('/home/rustem/projs/strategies/data/ani.mp4')
mpf.show()
