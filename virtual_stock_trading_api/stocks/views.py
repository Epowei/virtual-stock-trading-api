from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
from .models import Stock
from .serializers import StockSerializer, StockSearchSerializer
from .services import FinnhubService

# Stock App ViewSet

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['symbol']
    search_fields = ['symbol', 'company_name']
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        serializer = StockSearchSerializer(data=request.data)
        if serializer.is_valid():
            symbol = serializer.validated_data['symbol']
            finnhub_service = FinnhubService()
            
            # Try to get stock from database first
            try:
                stock = Stock.objects.get(symbol=symbol.upper())
                
                # Update stock price from Finnhub
                stock_data = finnhub_service.get_quote(symbol)
                if stock_data and 'c' in stock_data:
                    stock.last_price = stock_data['c']
                    stock.save()
                    
                return Response(StockSerializer(stock).data)
                
            except Stock.DoesNotExist:
                # Stock not in database, try to get from Finnhub
                stock_data = finnhub_service.get_quote(symbol)
                company_data = finnhub_service.get_company_profile(symbol)
                
                if stock_data and 'c' in stock_data and company_data and 'name' in company_data:
                    stock = Stock.objects.create(
                        symbol=symbol.upper(),
                        company_name=company_data['name'],
                        last_price=stock_data['c']
                    )
                    return Response(StockSerializer(stock).data)
                else:
                    return Response(
                        {"error": "Stock not found or couldn't retrieve data"},
                        status=status.HTTP_404_NOT_FOUND
                    )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def refresh_price(self, request, pk=None):
        stock = self.get_object()
        finnhub_service = FinnhubService()
        stock_data = finnhub_service.get_quote(stock.symbol)
        
        if stock_data and 'c' in stock_data:
            stock.last_price = stock_data['c']
            stock.save()
            return Response(StockSerializer(stock).data)
        else:
            return Response(
                {"error": "Couldn't retrieve updated price"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
