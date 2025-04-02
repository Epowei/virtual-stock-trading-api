from rest_framework import serializers
from .models import Portfolio, Position, Transaction, PortfolioSnapshot
from stocks.serializers import StockSerializer

class PositionSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.company_name', read_only=True)
    current_price = serializers.DecimalField(source='stock.last_price', max_digits=15, decimal_places=2, read_only=True)
    current_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    profit_loss = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    profit_loss_percentage = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Position
        fields = ['id', 'stock', 'stock_symbol', 'stock_name', 'quantity', 
                  'average_buy_price', 'current_price', 'current_value', 
                  'profit_loss', 'profit_loss_percentage']
        read_only_fields = ['id', 'average_buy_price']
        extra_kwargs = {
            'stock': {'write_only': True}
        }

class TransactionSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'stock', 'stock_symbol', 'transaction_type', 
                  'quantity', 'price', 'timestamp', 'total_amount']
        read_only_fields = ['id', 'timestamp', 'total_amount']

class PortfolioSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioSnapshot
        fields = ['id', 'date', 'cash_balance', 'stock_value', 'total_value']
        read_only_fields = ['id', 'date']

class PortfolioSerializer(serializers.ModelSerializer):
    positions_count = serializers.SerializerMethodField()
    total_stock_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'description', 'cash_balance', 
                  'positions_count', 'total_stock_value', 'total_value', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_positions_count(self, obj):
        return obj.positions.count()

class PortfolioDetailSerializer(PortfolioSerializer):
    positions = PositionSerializer(many=True, read_only=True)
    
    class Meta(PortfolioSerializer.Meta):
        fields = PortfolioSerializer.Meta.fields + ['positions']