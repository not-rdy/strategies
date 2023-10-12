import os
import pandas as pd
from tinkoff.invest import CandleInterval
from utils import get_init_historic_candles, get_init_df_candles
from datetime import datetime
from time import sleep
from tqdm import tqdm


class SignalMaker:

    def __init__(self) -> None:
        self.seq_prob = None

    @staticmethod
    def __prepare_target(candles: pd.DataFrame) -> pd.Series:
        candles['ts'] = candles['ts'].astype('datetime64[ns]')
        candles = candles.sort_values(by='ts')
        candles['target'] = candles['c'].diff()
        candles = candles.dropna()
        candles['target'] = candles['target']\
            .map(lambda x: '1' if x > 0 else '0' if x == 0 else '-1')
        target = candles.set_index('ts')['target']
        return target

    @staticmethod
    def __make_sequences(
            target: pd.Series, window: int,
            probas_threshold: float) -> pd.DataFrame:
        sequences = []
        for i in tqdm(
                range(0, target.shape[0] - window),
                total=target.shape[0] - window):
            sequences.append(
                {
                    'seq': target.iloc[i:i+window].sum(),
                    'next': target.iloc[i+window]
                }
            )

        dfseq = pd.DataFrame(sequences)
        dfseq['cnt'] = 1

        aggby_seq_next = dfseq.groupby(['seq', 'next'])['cnt'].sum()
        aggby_seq = dfseq.groupby('seq')['cnt'].sum()
        probas = aggby_seq_next / aggby_seq
        probas.name = 'probas'

        df = pd.concat([aggby_seq_next, probas], axis=1)
        df = df[df['probas'] > probas_threshold].reset_index()
        return df

    def fit(self,
            figi: str,
            interval: CandleInterval,
            from_: datetime, to_: datetime,
            probas_threshold: float, seq_window: int) -> None:

        timescale = pd.date_range(
            start=from_, end=to_, freq='M').to_pydatetime().tolist()

        dfs_list = []
        for left, right in tqdm(
                zip(timescale[:-1], timescale[1:]), total=len(timescale) - 1):

            sleep(5)
            candles = get_init_historic_candles(
                token=os.getenv('TOKEN'),
                figi=figi,
                interval=interval,
                from_=left,
                to_=right
            )
            candles = get_init_df_candles(candles)

            dfs_list.append(candles)

        df_candles = pd.concat(dfs_list).reset_index(drop=True)
        target = self.__prepare_target(df_candles)

        self.seq_prob = self.__make_sequences(
            target, seq_window, probas_threshold)

    def make(self, sequence: str) -> str:
        if sequence is None:
            return None
        filtered = self.seq_prob[self.seq_prob['seq'] == sequence]
        if filtered.shape[0] == 0:
            return None
        return filtered['next'].item()
