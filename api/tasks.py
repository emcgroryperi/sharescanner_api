from celery import shared_task

from .submodels.download_models import CompanyModel




@shared_task
def update_company(symbol):

    CompanyModel.update_data(symbol)

