from calendar import week
import imp
from django.db import models
from datetime import datetime, timedelta, tzinfo

from django.utils import timezone

import pandas as pd
from api.submodels.company import CompanyModel
import yfinance as yf

from django.apps import apps
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
    def bulk_create(df, company):
        data = []
        company = company
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
