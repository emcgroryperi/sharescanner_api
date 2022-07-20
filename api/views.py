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

    from .analysis import identify_ema_crossovers

    identify_ema_crossovers()

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

    # CompanyModel.objects.all().delete()
    # print('deleting')
    # sleep(10)
    # print('resuming')
    
    companies = CompanyModel.get_market_list()


    for company in companies['ASX code']:
        update_company.delay(company + '.AX')
    # CompanyModel.update_data('CBA.AX')

    return JsonResponse('updating all companies', safe=False)




    


    