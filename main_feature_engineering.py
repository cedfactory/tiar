from lib.fimport import *
from lib.findicators import *
from lib.featureengineering import fprocessfeature,fbalance
from lib.fdatapreprocessing import fdataprep
import numpy as np

import pandas as pd
import os

from rich import print,inspect

def get_real_dataframe():
    filename = "./lib/data/test/google_stocks_data.csv"
    df = fimport.GetDataFrameFromCsv(filename)
    df = findicators.normalize_column_headings(df)
    return df

def get_synthetic_dataframe():
    y = synthetic.get_sinusoid(length=5, amplitude=1, frequency=.1, phi=0, height = 0)
    df = synthetic.create_dataframe(y, 0.)
    df = findicators.normalize_column_headings(df)
    return df

def check(action):
    print("check \"{}\"".format(action))
    
    if action == "smote":
        df = get_real_dataframe()
        df = df.head(200)
        df = findicators.add_technical_indicators(df, ['trend_1d'])
        df = df.astype({"trend_1d": int})
        print(df.head())
        print(df['trend_1d'].value_counts())

        df = fbalance.smote_balance(df, 'trend_1d')
        df = findicators.remove_features(df, ["high", "low", "open", "close", "adj_close", "volume"])
        print(df.head())
        print(df['trend_1d'].value_counts())
        #df.to_csv("./lib/data/test/featureengineering_smote_reference.csv")


_usage_str = """
Options:
    [--check [process]]
process \in [smote]
"""

def _usage():
    print(_usage_str)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check" and len(sys.argv) > 2: check(sys.argv[2])
        else: _usage()
    else: _usage()