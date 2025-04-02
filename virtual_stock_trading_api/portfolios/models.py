from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from stocks.models import Stock

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('10000.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    @property
    def total_stock_value(self):
        return sum(position.current_value for position in self.positions.all())
    
    @property
    def total_value(self):
        return self.cash_balance + self.total_stock_value

class Position(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='positions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='positions')
    quantity = models.PositiveIntegerField()
    average_buy_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        unique_together = ('portfolio', 'stock')
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.stock.symbol} ({self.quantity})"
    
    @property
    def current_value(self):
        return Decimal(str(self.stock.last_price)) * Decimal(str(self.quantity))
    
    @property
    def profit_loss(self):
        current_total = self.current_value
        cost_basis = Decimal(str(self.average_buy_price)) * Decimal(str(self.quantity))
        return current_total - cost_basis
    
    @property
    def profit_loss_percentage(self):
        cost_basis = Decimal(str(self.average_buy_price)) * Decimal(str(self.quantity))
        if cost_basis == 0:
            return Decimal('0')
        return (self.profit_loss / cost_basis) * 100

class Transaction(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    TRANSACTION_TYPES = [
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.stock.symbol} at ${self.price}"
    
    @property
    def total_amount(self):
        return Decimal(str(self.price)) * Decimal(str(self.quantity))

class PortfolioSnapshot(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='snapshots')
    date = models.DateField(auto_now_add=True)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2)
    stock_value = models.DecimalField(max_digits=15, decimal_places=2)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        unique_together = ('portfolio', 'date')
    
    def __str__(self):
        return f"{self.portfolio.name} snapshot on {self.date}"
