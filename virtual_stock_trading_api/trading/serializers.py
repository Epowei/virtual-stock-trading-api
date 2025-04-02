from rest_framework import serializers

class TradeSerializer(serializers.Serializer):
    portfolio_id = serializers.IntegerField()
    stock_symbol = serializers.CharField(max_length=10)
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive")
        return value