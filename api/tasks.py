from celery import shared_task

from .submodels.company import CompanyModel




@shared_task
def update_company(symbol):

    CompanyModel.update_data(symbol)

