from celery import shared_task

from .submodels.company import CompanyModel




@shared_task
def update_company(symbol):
    print(f'{symbol} is now updating')
    CompanyModel.update_data(symbol)


# def identify_ema_crossovers():
