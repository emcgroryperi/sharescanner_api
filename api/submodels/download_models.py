from calendar import week
from django.db import models
from datetime import datetime, timedelta, tzinfo

from django.utils import timezone

import pandas as pd
import yfinance as yf

def two_years_ago():
    return timezone.now() - timezone.timedelta(weeks=104)

class CompanyModel(models.Model):
    """A class to define a company listed on some stock exchange"""

    # users = models.ManyToManyField(User)

    # Set date to current time, should be overwritten when data is downloaded
    name = models.CharField(max_length=50, help_text="Name of the company")
    exchange = models.CharField(
        max_length=20,
        help_text="Symbol used on the market (ASX for Australian Stock Exchange)",
    )
    symbol = models.CharField(
        max_length=20,
        help_text="Symbol to be used on the market (eg FMG.AX for Fortescue on ASX)",
        primary_key=True,
    )
    market_cap = models.BigIntegerField()
    last_updated = models.DateTimeField(default=two_years_ago)

    def __str__(self):
        return self.symbol + ' ' + self.name
        
    """ Creates a new instance and stores it in the database """
    @classmethod
    def create(self, symbol, period="2y"):
        # Checks to see if it exists in the database

        company = self()
        company.symbol = symbol

        ticker = yf.Ticker(symbol).info

        company.market_cap = ticker["marketCap"]
        company.exchange = ticker["exchange"]
        company.name = ticker["longName"]
        company.last_updated = two_years_ago()

        company.save()

        print(f"{symbol} has been created")

        return company


    @staticmethod
    def update_data(symbol):
        print(f"updating {symbol} ")
        
        # The data already exists in the database
        try:
            company = CompanyModel.get(symbol)
        except CompanyModel.DoesNotExist:
            try:
                company = CompanyModel.create(symbol)
            except:
                print(f'Error creating company {symbol}')
                return

        # If the last date has already been downloaded then skip it
        if (timezone.now() - company.last_updated).days == 0:
            print(f"{symbol} up to date")
            return

        print('Downloading data')

        # Download from one day after the last day
        ticker = yf.Ticker(symbol)

        updated_data = ticker.history(start=(company.last_updated + timezone.timedelta(days=1)))
        updated_data.reset_index(inplace=True)

        company.last_updated = timezone.now()
        company.save()

        HistoricalPrices.bulk_create(updated_data, symbol)
        print(f'{symbol} successfully updated')
        return

    
    def get_data(self, earliest_date=None):

        if earliest_date is not None:
            data = self.historicalprices_set.filter(date__gte=datetime.strptime(earliest_date, '%Y-%m-%d'))
        else:
            data = self.historicalprices_set.all()
        
        return data
   

    @staticmethod
    def get(symbol):
        company = CompanyModel.objects.get(pk=symbol)
        return company

    
    @staticmethod
    def retrieve_company_list():

        companies = list(CompanyModel.objects.all())

        return companies

    def get_market_list():
        """Download a list of the ASX markets and return a sorted pandas dataframe"""

        asx_data = pd.read_csv('https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file?access_token=83ff96335c2d45a094df02a206a39ff4')

        # Sorts the data and rewrites it to a new dataframe sorted by market capitilisation
        # Top 200 markets will represent the ASX 200 etc...
        asx_sorted = asx_data.sort_values(["Market Cap"], ascending=False)[0:200]
        asx_sorted = asx_sorted.reset_index()

        return asx_sorted



class HistoricalPrices(models.Model):
    
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.IntegerField()
    dividends = models.FloatField()
    stock_splits = models.IntegerField()
    company = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)

    class Meta:
        models.UniqueConstraint(name="Date company", fields=['date','company'])
        ordering = ["date"]

    def __str__(self):
        return f"{self.date, self.open, self.company, self.volume}"

    @staticmethod
    def bulk_create(df, company_symbol):
        data = []
        company = CompanyModel.get(company_symbol)
        for index, day in df.iterrows():
            price = HistoricalPrices()
            price.date = day['Date'].strftime('%Y-%m-%d')
            price.open = day['Open']
            price.high = day['High']
            price.low = day['Low']
            price.close = day['Close']
            price.volume = day['Volume']
            price.dividends = day['Dividends']
            price.stock_splits = 0
            price.company = company

            data.append(price)
        HistoricalPrices.objects.bulk_create(data)    
        return
