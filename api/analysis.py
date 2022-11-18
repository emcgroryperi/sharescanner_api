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

    volume_peaks = data[data['volume'] > (vol_mean + 2.5*vol_std)][['volume', 'date']]
    
    volume_peaks['strength'] = (volume_peaks['volume']-vol_mean) / vol_std

    return volume_peaks


def recent_volume_peaks(company_symbol, data, max_age=7):
    company_peak = volume_peaks(data)
    company_peak['company'] = company_symbol

    recent_peaks = company_peak[company_peak['date'] > (datetime.now() - timedelta(max_age)).date()].copy()
    # print(company_peak)
    
    # print('trying something?')
    recent_peaks['info'] = recent_peaks['strength']
    recent_peaks['info_label'] = 'standard deviations above mean'
    recent_peaks['type'] = 'volume'
    return recent_peaks[['company','date','info', 'info_label', 'type']]


 
def market_scan(indicators):
    companies = CompanyModel.get_company_list()[0:50]
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
            if len(result.index) != 0:
                flags = pd.concat([flags, result], ignore_index=True)

    flags = flags.drop_duplicates(ignore_index=True)
    
    print(flags)

    return flags







# def identify_ema_crossovers(age=7, short=10, long=50):
#     companies = CompanyModel.get_company_list()
#     crossovers = pd.DataFrame(columns=['date', 'company', 'info'])
#     # age = 7
#     # for company in companies:
#     #     cross = ema_crossovers(company.symbol, short, long)
#     #     if len(cross) != 0:
#     #         recent_crosses = cross[cross['date'] > (datetime.now() - timedelta(age)).date()].copy()
#     #         recent_crosses['company'] = company.symbol
#     #         crossovers = pd.concat([crossovers,recent_crosses[['company', 'date', 'diff']]], ignore_index=True)
# return crossovers


# def identify_volume_peaks(age=7):
#     companies = CompanyModel.get_company_list()
#     peaks = pd.DataFrame(columns=['date', 'company', 'strength'])
#     age = 7

#     # for company in companies:
#     #     company_peak = volume_peaks(company.symbol, period=age)
#     #     company_peak['company'] = company.symbol

#     #     if len(company_peak) != 0:
#     #         recent_peaks = company_peak[company_peak['date'] > (datetime.now() - timedelta(age)).date()].copy()
#     #         peaks = pd.concat([peaks,recent_peaks], ignore_index=True, verify_integrity=True)

#     # peaks = peaks.drop_duplicates(ignore_index=True)[['company', 'date', 'volume', 'strength']]
    
#     print(peaks)

#     return peaks
