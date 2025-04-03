from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from .models import Portfolio, Position, Transaction, PortfolioSnapshot
from .serializers import (PortfolioSerializer, PortfolioDetailSerializer, 
                         PositionSerializer, TransactionSerializer,
                         PortfolioSnapshotSerializer)
from .tasks import create_portfolio_snapshot

# Portfolios viewset

class PortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PortfolioDetailSerializer
        return PortfolioSerializer
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        portfolio = self.get_object()
        transactions = Transaction.objects.filter(portfolio=portfolio).order_by('-timestamp')
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def snapshots(self, request, pk=None):
        portfolio = self.get_object()
        snapshots = PortfolioSnapshot.objects.filter(portfolio=portfolio).order_by('-date')
        page = self.paginate_queryset(snapshots)
        if page is not None:
            serializer = PortfolioSnapshotSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PortfolioSnapshotSerializer(snapshots, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_snapshot(self, request, pk=None):
        portfolio = self.get_object()
        try:
            # Instead of using Celery task, directly create snapshot
            stock_value = portfolio.total_stock_value
            total_value = portfolio.total_value
            
            PortfolioSnapshot.objects.create(
                portfolio=portfolio,
                cash_balance=portfolio.cash_balance,
                stock_value=stock_value,
                total_value=total_value
            )
            return Response({'status': 'snapshot created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Position.objects.filter(portfolio__user=self.request.user)
