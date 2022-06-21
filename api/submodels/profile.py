
import json

from django.contrib.auth.models import User
from django.db import models

from .download_models import CompanyModel

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_list = models.ManyToManyField(CompanyModel)
    filter_companies = models.BooleanField(default=False)

    indicators = models.CharField(default="{}", max_length=1000)

    def add_indicators(self, indicator_object):
        """Tuples should be in the form of {name, func, kwargs}"""
        try:
            indic = json.loads(self.indicators)
        except json.decoder.JSONDecodeError:
            self.indicators = "{}"

        indic[len(indic)] = indicator_object
        str_dict = json.dumps(indic)
        self.indicators = str_dict
        indic = json.loads(self.indicators)

        self.save()

    def get_indicators(self):
        try:
            indic = json.loads(self.indicators)
        except json.decoder.JSONDecodeError:
            self.indicators = "{}"

        return json.loads(self.indicators)

    def reset_indicators(self):
        self.indicators = "{}"
        self.save()

    def reset_list(self):
        self.filter_companies = False
        self.company_list.clear()
        print(self.company_list)
        self.save()

    def filter_list(self):
        self.filter_companies = True
        self.save()

    def check_filter(self):
        return self.filter_companies

    def get_companies(self):
        if self.filter_companies:
            return list(self.company_list.all())
        else:
            return CompanyModel.retrieve_all()

    def __str__(self):
        return f"[ {self.company_list} ]"