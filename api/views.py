from time import sleep
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .submodels.company import CompanyModel
import pandas as pd
from .serializers import CompanySerializer, CompanyDataSerializer

from .tasks import update_company

""" Returns a single company as a json with it's data """
def company(request, company):

    company = company + '.AX'

    result = {}
    result['company'] = CompanyModel.get(company)
    result['data'] = result['company'].get_data('2022-01-01')


    output = CompanyDataSerializer(result)

    return JsonResponse(output.data)


def update(request):

    update_company.delay('IAG.AX')

    return JsonResponse('updated', safe=False)


""" Returns all the current companies that are currently stored """
def companies(request):

    companies = CompanyModel.objects.all()
    # serialize the company data
    serializer = CompanySerializer(companies, many=True)
    # return a Json response
    return JsonResponse(serializer.data, safe=False)


def update_companies(request):
    
    companies = CompanyModel.get_market_list()

    for company in companies['ASX code']:
        update_company.delay(company + '.AX')

    return JsonResponse('updating all companies', safe=False)


def perform_market_scan(request): 

    # if request.method != 'POST':
    #     return JsonResponse('error', safe=False)


    
    from .analysis import market_scan


    indicators = [
        {
            "key": "EMA_10_50",
            "filter": "EMA crossover",
            "short_ema": "10",
            "long_ema": "50"
        },
        {
            "key": "EMA_8_20",
            "filter": "EMA crossover",
            "short_ema": "8",
            "long_ema": "20"
        },
        {
            "key": "volume",
            "filter": "Volume Peaks"
        }
    ]
    flags = market_scan(indicators)

    return JsonResponse(flags.to_json(orient='split', date_format='iso'), safe=False)


    