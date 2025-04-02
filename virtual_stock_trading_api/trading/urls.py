from django.urls import path
from .views import BuyStockView, SellStockView

urlpatterns = [
    path('buy/', BuyStockView.as_view(), name='buy-stock'),
    path('sell/', SellStockView.as_view(), name='sell-stock'),
]