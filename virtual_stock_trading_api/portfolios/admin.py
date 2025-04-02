from django.contrib import admin
from .models import Portfolio, Position, Transaction, PortfolioSnapshot

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'cash_balance', 'created_at']
    search_fields = ['name', 'user__username']
    list_filter = ['created_at']

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'stock', 'quantity', 'average_buy_price']
    search_fields = ['portfolio__name', 'stock__symbol']
    list_filter = ['portfolio']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'stock', 'transaction_type', 'quantity', 'price', 'timestamp']
    search_fields = ['portfolio__name', 'stock__symbol']
    list_filter = ['transaction_type', 'timestamp', 'portfolio']

@admin.register(PortfolioSnapshot)
class PortfolioSnapshotAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'date', 'cash_balance', 'stock_value', 'total_value']
    search_fields = ['portfolio__name']
    list_filter = ['date', 'portfolio']
