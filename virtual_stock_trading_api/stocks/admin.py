from django.contrib import admin
from .models import Stock

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'company_name', 'last_price', 'last_updated']
    search_fields = ['symbol', 'company_name']
    list_filter = ['last_updated']
