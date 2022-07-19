from genericpath import exists
from .submodels.company import CompanyModel

from datetime import datetime, timedelta

import numpy as np 
import pandas as pd
import pandas_ta as ta
pd.set_option('display.max_rows', None)
# Two months
minimum_time = 60

# Gets the EMA of the company over a specified period of the last two months
def get_ema(company_symbol, period):
    date = (datetime.now() - timedelta(days=minimum_time+period)).strftime('%Y-%m-%d')
    data = CompanyModel.get(company_symbol).get_df()
    ema = ta.ema(data['close'], period)
    df = pd.DataFrame()
    df['EMA'] = ema
    df['date'] = data['date']

    return df

# Gets the bbands of the last two months
def get_bbands(company_symbol, period, std):
    date = (datetime.now() - timedelta(days=minimum_time+period)).strftime('%Y-%m-%d')
    data = CompanyModel.get(company_symbol).get_df(date)
    bbands = ta.bbands(data['close'], period, std)
    return bbands

def ema_crossovers(company_symbol, short, long):
    short_ema = get_ema(company_symbol, short)
    long_ema = get_ema(company_symbol, long)

    short_length = len(short_ema)
    long_length = len(long_ema)
    comparison = pd.Series(np.where(short_ema['EMA'][(short_length-minimum_time):].reset_index(drop=True) > long_ema['EMA'][(long_length-minimum_time):].reset_index(drop=True), 1.0, 0.0))
    # print(comparison)
    diff = pd.DataFrame()
    diff['diff'] = comparison.diff()
    diff['date'] = long_ema['date'][(long_length-minimum_time):].reset_index(drop=True)
    print(diff[1:][(diff[1:]['diff'] != 0) ])    
