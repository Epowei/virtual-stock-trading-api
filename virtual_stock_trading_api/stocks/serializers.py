from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'company_name', 'last_price', 'last_updated']
        read_only_fields = ['id', 'last_updated']

class StockSearchSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=10)