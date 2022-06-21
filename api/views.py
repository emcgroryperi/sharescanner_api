from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .submodels.download_models import CompanyModel

from .serializers import CompanySerializer, CompanyDataSerializer

from .tasks import update_company

""" Returns a single company as a json with it's data """
def company(request):

    result = {}
    result['company'] = CompanyModel.get('CBA.AX')
    result['data'] = result['company'].get_data('2022-04-01')

    output = CompanyDataSerializer(result)

    return JsonResponse(output.data)


def update(request):

    CompanyModel.update_data('CBA.AX')

    return JsonResponse('updated', safe=False)


""" Returns all the current companies that are currently stored """
def companies(request):

    companies = CompanyModel.objects.all()
    # serialize the company data
    serializer = CompanySerializer(companies, many=True)
    # return a Json response
    return JsonResponse(serializer.data, safe=False)


