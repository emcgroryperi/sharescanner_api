from rest_framework import routers, serializers, viewsets
from .submodels.download_models import CompanyModel, HistoricalPrices


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CompanyModel
        fields = ['name', 'exchange', 'symbol', 'market_cap', 'last_updated']

class HistoricalPricesSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = HistoricalPrices
        fields = ['date', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits' ]

class CompanyDataSerializer(serializers.Serializer):
    
    company = CompanySerializer()
    data = HistoricalPricesSerializer(many=True)
    