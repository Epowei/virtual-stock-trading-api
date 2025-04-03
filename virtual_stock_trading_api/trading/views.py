from django.shortcuts import render
from decimal import Decimal
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from portfolios.models import Portfolio, Position, Transaction
from stocks.models import Stock
from stocks.services import FinnhubService
from .serializers import TradeSerializer

# Trading Viewsets

class BuyStockView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TradeSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        portfolio_id = serializer.validated_data['portfolio_id']
        stock_symbol = serializer.validated_data['stock_symbol'].upper()
        quantity = serializer.validated_data['quantity']
        
        try:
            # Check if portfolio belongs to the user
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        except Portfolio.DoesNotExist:
            return Response(
                {"error": "Portfolio not found or access denied"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        try:
            # Get or create the stock
            stock, created = Stock.objects.get_or_create(symbol=stock_symbol)
            
            # If stock was just created or doesn't have a price, fetch it from Finnhub
            if created or stock.last_price == Decimal('0.00'):
                finnhub_service = FinnhubService()
                stock_data = finnhub_service.get_quote(stock_symbol)
                company_data = finnhub_service.get_company_profile(stock_symbol)
                
                if not stock_data or 'c' not in stock_data:
                    return Response(
                        {"error": "Could not retrieve stock price"},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                    
                stock.last_price = Decimal(str(stock_data['c']))
                
                if company_data and 'name' in company_data:
                    stock.company_name = company_data['name']
                elif not stock.company_name:
                    stock.company_name = stock_symbol
                    
                stock.save()
            
            current_price = stock.last_price
            total_cost = current_price * Decimal(str(quantity))
            
            # Check if enough cash in portfolio
            if portfolio.cash_balance < total_cost:
                return Response(
                    {"error": "Insufficient funds in portfolio"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Execute the trade
            with transaction.atomic():
                # Update portfolio cash balance
                portfolio.cash_balance -= total_cost
                portfolio.save()
                
                # Update or create position
                position, created = Position.objects.get_or_create(
                    portfolio=portfolio,
                    stock=stock,
                    defaults={
                        'quantity': quantity,
                        'average_buy_price': current_price
                    }
                )
                
                if not created:
                    # Update average purchase price
                    total_shares = position.quantity + quantity
                    position.average_buy_price = (
                        (position.quantity * position.average_buy_price) + 
                        (quantity * current_price)
                    ) / total_shares
                    position.quantity = total_shares
                    position.save()
                
                # Record the transaction
                Transaction.objects.create(
                    portfolio=portfolio,
                    stock=stock,
                    transaction_type=Transaction.BUY,
                    quantity=quantity,
                    price=current_price
                )
                
            return Response({
                "message": f"Successfully bought {quantity} shares of {stock_symbol} at ${current_price}",
                "portfolio_balance": portfolio.cash_balance,
                "transaction_total": total_cost,
                "current_position": {
                    "symbol": stock.symbol,
                    "quantity": position.quantity,
                    "average_price": position.average_buy_price
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SellStockView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TradeSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        portfolio_id = serializer.validated_data['portfolio_id']
        stock_symbol = serializer.validated_data['stock_symbol'].upper()
        quantity = serializer.validated_data['quantity']
            
        try:
            # Check if portfolio belongs to the user
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        except Portfolio.DoesNotExist:
            return Response(
                {"error": "Portfolio not found or access denied"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        try:
            # Get the stock
            stock = Stock.objects.get(symbol=stock_symbol)
            
            # Check if position exists and has enough shares
            try:
                position = Position.objects.get(portfolio=portfolio, stock=stock)
                if position.quantity < quantity:
                    return Response(
                        {"error": f"Not enough shares to sell. You have {position.quantity} shares."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Position.DoesNotExist:
                return Response(
                    {"error": "You don't own any shares of this stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Update stock price from Finnhub
            finnhub_service = FinnhubService()
            stock_data = finnhub_service.get_quote(stock_symbol)
            
            if stock_data and 'c' in stock_data:
                stock.last_price = Decimal(str(stock_data['c']))
                stock.save()
                
            current_price = stock.last_price
            total_value = current_price * Decimal(str(quantity))
            
            # Execute the trade
            with transaction.atomic():
                # Update portfolio cash balance
                portfolio.cash_balance += total_value
                portfolio.save()
                
                # Update position
                position.quantity -= quantity
                if position.quantity == 0:
                    position.delete()
                    position_data = "No position"
                else:
                    position.save()
                    position_data = {
                        "symbol": stock.symbol,
                        "quantity": position.quantity,
                        "average_price": position.average_buy_price
                    }
                
                # Record the transaction
                Transaction.objects.create(
                    portfolio=portfolio,
                    stock=stock,
                    transaction_type=Transaction.SELL,
                    quantity=quantity,
                    price=current_price
                )
                
            return Response({
                "message": f"Successfully sold {quantity} shares of {stock_symbol} at ${current_price}",
                "portfolio_balance": portfolio.cash_balance,
                "transaction_total": total_value,
                "current_position": position_data
            }, status=status.HTTP_200_OK)
            
        except Stock.DoesNotExist:
            return Response(
                {"error": f"Stock with symbol {stock_symbol} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
