from celery import shared_task
from django.db import transaction
from .models import Portfolio, PortfolioSnapshot

@shared_task
def create_daily_portfolio_snapshots():
    """
    Create snapshots for all portfolios
    """
    portfolios = Portfolio.objects.all()
    for portfolio in portfolios:
        create_portfolio_snapshot(portfolio.id)
    return f"Created snapshots for {len(portfolios)} portfolios"

@shared_task
def create_portfolio_snapshot(portfolio_id):
    """
    Create a snapshot for a specific portfolio
    """
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id)
        stock_value = portfolio.total_stock_value
        total_value = portfolio.total_value
        
        with transaction.atomic():
            PortfolioSnapshot.objects.create(
                portfolio=portfolio,
                cash_balance=portfolio.cash_balance,
                stock_value=stock_value,
                total_value=total_value
            )
        
        return f"Created snapshot for portfolio {portfolio.name}"
    except Portfolio.DoesNotExist:
        return f"Portfolio with ID {portfolio_id} not found"
    except Exception as e:
        return f"Error creating snapshot: {str(e)}"