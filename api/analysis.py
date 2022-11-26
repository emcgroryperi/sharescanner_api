from api.submodels.price import HistoricalPrices
from .submodels.company import CompanyModel

from datetime import datetime, timedelta

import numpy as np 
import pandas as pd
import pandas_ta as ta
pd.set_option('display.max_rows', None)
# Two months
minimum_time = 60

# Gets the EMA of the company over a specified period of the last two months
def get_ema(data, period=20):
    ema = ta.ema(data['close'], period)
    df = pd.DataFrame()
    df['EMA'] = ema
    df['date'] = data['date']

    return df

# Gets the bbands of the last two months
def get_bbands(data, period=20, std=2):
    date = (datetime.now() - timedelta(days=minimum_time+period)).strftime('%Y-%m-%d')
    bbands = ta.bbands(data['close'], period, std)
    return bbands

def ema_crossovers(data, short, long):
    short_ema = get_ema(data, short)
    long_ema = get_ema(data, long)

    short_length = len(short_ema)
    long_length = len(long_ema)
    comparison = pd.Series(np.where(short_ema['EMA'][(short_length-minimum_time):].reset_index(drop=True) > long_ema['EMA'][(long_length-minimum_time):].reset_index(drop=True), 1.0, 0.0))
    # print(comparison)
    diff = pd.DataFrame()
    diff['info'] = comparison.diff()
    diff['date'] = long_ema['date'][(long_length-minimum_time):].reset_index(drop=True)
    crossovers = diff[1:][(diff[1:]['info'] == 1) ]    

    return crossovers[['date', 'info']]


def recent_ema_crossovers(company_symbol, company_data, age=7, short_ema=10, long_ema=50):
    result = ema_crossovers(company_data, short_ema, long_ema)
    result['company'] = company_symbol

    recent_results = result[result['date'] > (datetime.now() - timedelta(age)).date()].copy()
    recent_results['type'] = 'ema_crossovers'
    recent_results['info_label'] = 'Positive or Negative crossover'
    return recent_results[['company', 'date', 'info', 'info_label', 'type']]
    


    

def volume_peaks(data): 
    # date = (datetime.now() - timedelta(days=minimum_time+period)).strftime('%Y-%m-%d')

    vol_std = np.std(data['volume'])
    vol_mean = np.mean(data['volume'])

    volume_peaks = data[data['volume'] > (vol_mean + 3*vol_std)][['volume', 'date']]
    
    volume_peaks['strength'] = (volume_peaks['volume']-vol_mean) / vol_std

    return volume_peaks


def recent_volume_peaks(company_symbol, data, max_age=7):
    company_peak = volume_peaks(data)
    company_peak['company'] = company_symbol

    recent_peaks = company_peak[company_peak['date'] > (datetime.now() - timedelta(max_age)).date()].copy()

    recent_peaks['info'] = recent_peaks['strength']
    recent_peaks['info_label'] = 'standard deviations above mean'
    recent_peaks['type'] = 'volume'
    return recent_peaks[['company','date','info', 'info_label', 'type']]


def recent_rsi_crosses(company_symbol, data, max_age=7):
    rsi = ta.rsi(data['close'])

    rsi_crosses = data[['date']].copy()
    rsi_crosses['rsi'] = rsi

    rsi_crosses['company'] = company_symbol

    overbought = rsi_crosses[(rsi_crosses['rsi'] > 70)].copy()
    overbought['info'] = overbought['rsi']
    oversold = rsi_crosses[rsi_crosses['rsi'] < 30].copy()
    oversold['info'] = oversold['rsi']

    recent_rsi_crosses = pd.concat([overbought, oversold], ignore_index=True)
    recent_rsi_crosses['type'] = 'rsi'
    recent_rsi_crosses['info_label'] = 'Overbought or Oversold'

    rsis = recent_rsi_crosses[recent_rsi_crosses['date'] > (datetime.now() - timedelta(max_age)).date()].copy()

    return rsis[['company','date','info', 'info_label', 'type']]
 
def market_scan(indicators):
    companies = CompanyModel.get_company_list()
    flags = pd.DataFrame(columns=['company', 'date', 'info','info_label', 'type', 'filter'])
    age = 7
    result = pd.DataFrame(columns=['company', 'date', 'info', 'info_label', 'type'])
    for company in companies:
        company_data = CompanyModel.get(company.symbol).get_df()

        for indicator in indicators:
            age = indicator['age'] if 'age' in indicator.keys() else 7
            if indicator['filter'] == 'EMA crossover':
                result = recent_ema_crossovers(company.symbol, 
                                        company_data, 
                                        age=age,
                                        short_ema=int(indicator['short_ema']), 
                                        long_ema=int(indicator['long_ema']))
                result['filter'] = indicator['key']
            if indicator['filter'] == 'Volume Peaks':
                result = recent_volume_peaks(company.symbol, company_data, max_age=age)
                result['filter'] = indicator['key']
            if indicator['filter'] == 'RSI thresholds':
                result = recent_rsi_crosses(company.symbol, company_data, max_age=age)
                result['filter'] = indicator['key']
        if len(result.index) != 0:
            flags = pd.concat([flags, result], ignore_index=True)

    flags = flags.drop_duplicates(ignore_index=True)
    
    print(flags)

    return flags


