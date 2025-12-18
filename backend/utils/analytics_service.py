"""
Advanced Analytics Service
Phase 7: Advanced Features - M7.3: Advanced Analytics & Insights

Provides predictive analytics, forecasting, and benchmarking.
Currently uses seed data and statistical calculations.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import func
from models.database import db, Client, Trainer, Session, Payment, Goal
from utils.logger import logger
import random

def predict_client_churn(client_id: int, days_lookback: int = 90) -> Dict[str, Any]:
    """
    Predict client churn probability
    
    Args:
        client_id: Client ID
        days_lookback: Number of days to look back for analysis
    
    Returns:
        Churn prediction with probability and factors
    """
    client = Client.query.get(client_id)
    if not client:
        return {'error': 'Client not found'}
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_lookback)
        
        # Get recent sessions
        recent_sessions = Session.query.filter(
            Session.client_id == client_id,
            Session.session_date >= cutoff_date
        ).count()
        
        # Get recent payments
        recent_payments = Payment.query.filter(
            Payment.client_id == client_id,
            Payment.payment_date >= cutoff_date,
            Payment.status == 'completed'
        ).count()
        
        # Calculate churn factors
        session_frequency = recent_sessions / (days_lookback / 7)  # Sessions per week
        payment_frequency = recent_payments / (days_lookback / 30)  # Payments per month
        
        # Seed data-based prediction
        # In production, this would use ML models
        churn_probability = 0.0
        
        if session_frequency < 0.5:
            churn_probability += 0.4
        elif session_frequency < 1.0:
            churn_probability += 0.2
        
        if payment_frequency < 0.5:
            churn_probability += 0.3
        elif payment_frequency < 1.0:
            churn_probability += 0.15
        
        # Randomize slightly for seed data
        churn_probability = min(1.0, churn_probability + random.uniform(-0.1, 0.1))
        churn_probability = max(0.0, churn_probability)
        
        risk_level = 'low' if churn_probability < 0.3 else 'medium' if churn_probability < 0.6 else 'high'
        
        factors = []
        if session_frequency < 0.5:
            factors.append('Low session attendance')
        if payment_frequency < 0.5:
            factors.append('Irregular payments')
        if not factors:
            factors.append('Normal activity patterns')
        
        return {
            'client_id': client_id,
            'churn_probability': round(churn_probability, 2),
            'risk_level': risk_level,
            'factors': factors,
            'session_frequency': round(session_frequency, 2),
            'payment_frequency': round(payment_frequency, 2),
            'prediction_date': datetime.utcnow().isoformat(),
            'source': 'seed_data'
        }
        
    except Exception as e:
        logger.error(f"Error predicting churn: {str(e)}")
        return {'error': str(e)}

def forecast_revenue(months: int = 6) -> Dict[str, Any]:
    """
    Forecast revenue for the next N months
    
    Args:
        months: Number of months to forecast
    
    Returns:
        Revenue forecast with monthly predictions
    """
    try:
        # Get historical revenue data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get monthly revenue for past months
        monthly_revenue = db.session.query(
            func.extract('year', Payment.payment_date).label('year'),
            func.extract('month', Payment.payment_date).label('month'),
            func.sum(Payment.amount).label('total')
        ).filter(
            Payment.status == 'completed',
            Payment.payment_date >= start_date
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        # Calculate average monthly revenue
        if monthly_revenue:
            avg_monthly = sum(float(item.total) for item in monthly_revenue) / len(monthly_revenue)
        else:
            # Fallback to seed data
            avg_monthly = random.uniform(5000, 15000)
        
        # Generate forecast (simple trend projection)
        forecast = []
        current_date = datetime.utcnow()
        
        # Apply growth trend (seed data: slight positive trend)
        growth_rate = random.uniform(0.95, 1.05)  # -5% to +5% monthly
        
        for i in range(1, months + 1):
            forecast_month = current_date + timedelta(days=30 * i)
            projected_revenue = avg_monthly * (growth_rate ** i)
            
            # Add some variance
            projected_revenue *= random.uniform(0.9, 1.1)
            
            forecast.append({
                'month': forecast_month.strftime('%Y-%m'),
                'projected_revenue': round(projected_revenue, 2),
                'confidence': round(random.uniform(0.75, 0.95), 2)
            })
        
        total_forecast = sum(item['projected_revenue'] for item in forecast)
        
        return {
            'forecast_months': months,
            'monthly_forecast': forecast,
            'total_forecast': round(total_forecast, 2),
            'average_monthly': round(avg_monthly, 2),
            'growth_rate': round((growth_rate - 1) * 100, 2),
            'forecast_date': datetime.utcnow().isoformat(),
            'source': 'seed_data'
        }
        
    except Exception as e:
        logger.error(f"Error forecasting revenue: {str(e)}")
        return {'error': str(e)}

def benchmark_trainer_performance(trainer_id: int) -> Dict[str, Any]:
    """
    Benchmark trainer performance against averages
    
    Args:
        trainer_id: Trainer ID
    
    Returns:
        Performance benchmarks and comparisons
    """
    trainer = Trainer.query.get(trainer_id)
    if not trainer:
        return {'error': 'Trainer not found'}
    
    try:
        # Get trainer stats
        trainer_sessions = Session.query.filter_by(trainer_id=trainer_id).count()
        trainer_completed = Session.query.filter_by(
            trainer_id=trainer_id,
            status='completed'
        ).count()
        trainer_clients = db.session.query(func.count(func.distinct(Session.client_id))).filter_by(
            trainer_id=trainer_id
        ).scalar()
        
        # Get average stats across all trainers
        total_trainers = Trainer.query.filter_by(active=True).count()
        if total_trainers > 1:
            avg_sessions = Session.query.count() / total_trainers
            avg_completed = Session.query.filter_by(status='completed').count() / total_trainers
            avg_clients = db.session.query(
                func.count(func.distinct(Session.client_id))
            ).scalar() / total_trainers
        else:
            avg_sessions = trainer_sessions
            avg_completed = trainer_completed
            avg_clients = trainer_clients
        
        # Calculate performance metrics
        completion_rate = (trainer_completed / trainer_sessions * 100) if trainer_sessions > 0 else 0
        avg_completion_rate = (avg_completed / avg_sessions * 100) if avg_sessions > 0 else 0
        
        # Seed data: performance rating
        performance_score = random.uniform(70, 100)
        
        benchmarks = {
            'trainer_id': trainer_id,
            'trainer_name': trainer.name,
            'metrics': {
                'total_sessions': trainer_sessions,
                'completed_sessions': trainer_completed,
                'completion_rate': round(completion_rate, 1),
                'unique_clients': trainer_clients
            },
            'benchmarks': {
                'avg_sessions': round(avg_sessions, 1),
                'avg_completed': round(avg_completed, 1),
                'avg_completion_rate': round(avg_completion_rate, 1),
                'avg_clients': round(avg_clients, 1)
            },
            'performance_score': round(performance_score, 1),
            'rating': 'excellent' if performance_score >= 90 else 'good' if performance_score >= 75 else 'average',
            'benchmark_date': datetime.utcnow().isoformat(),
            'source': 'seed_data'
        }
        
        return benchmarks
        
    except Exception as e:
        logger.error(f"Error benchmarking trainer: {str(e)}")
        return {'error': str(e)}

def get_predictive_insights(days_lookback: int = 30) -> Dict[str, Any]:
    """
    Get predictive insights across the platform
    
    Args:
        days_lookback: Number of days to analyze
    
    Returns:
        Various predictive insights
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_lookback)
        
        # Get active clients
        active_clients = Client.query.filter_by(active=True).count()
        
        # Get clients at risk
        at_risk_clients = []
        clients = Client.query.filter_by(active=True).limit(10).all()
        
        for client in clients:
            recent_sessions = Session.query.filter(
                Session.client_id == client.id,
                Session.session_date >= cutoff_date
            ).count()
            
            if recent_sessions < 2:  # Less than 2 sessions in last 30 days
                at_risk_clients.append({
                    'client_id': client.id,
                    'client_name': client.name,
                    'risk_reason': 'Low session attendance'
                })
        
        # Revenue trend
        current_month_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.payment_date >= datetime.utcnow().replace(day=1)
        ).scalar() or 0
        
        last_month_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.payment_date >= (datetime.utcnow().replace(day=1) - timedelta(days=1)).replace(day=1),
            Payment.payment_date < datetime.utcnow().replace(day=1)
        ).scalar() or 0
        
        revenue_change = ((current_month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
        
        return {
            'insights': {
                'active_clients': active_clients,
                'at_risk_clients_count': len(at_risk_clients),
                'at_risk_clients': at_risk_clients[:5],  # Top 5
                'revenue_trend': {
                    'current_month': float(current_month_revenue),
                    'last_month': float(last_month_revenue),
                    'change_percent': round(revenue_change, 1),
                    'trend': 'up' if revenue_change > 0 else 'down' if revenue_change < 0 else 'stable'
                }
            },
            'analysis_date': datetime.utcnow().isoformat(),
            'source': 'seed_data'
        }
        
    except Exception as e:
        logger.error(f"Error getting predictive insights: {str(e)}")
        return {'error': str(e)}

