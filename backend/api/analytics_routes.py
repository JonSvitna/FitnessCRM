from flask import Blueprint, request, jsonify
from models.database import db, Client, Trainer, Session, Payment, Assignment, WorkoutLog
from sqlalchemy import func, extract, case
from datetime import datetime, timedelta
from utils.logger import logger

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Client Analytics

@analytics_bp.route('/clients/retention', methods=['GET'])
def get_client_retention():
    """Calculate client retention metrics"""
    try:
        # Get date range
        end_date = datetime.utcnow()
        start_date_month = end_date - timedelta(days=30)
        start_date_3months = end_date - timedelta(days=90)
        start_date_year = end_date - timedelta(days=365)
        
        # Total active clients
        total_active = Client.query.filter(Client.status == 'active').count()
        
        # Total clients (all time)
        total_clients = Client.query.count()
        
        # New clients this month
        new_this_month = Client.query.filter(
            Client.created_at >= start_date_month
        ).count()
        
        # Churned clients (inactive clients who were previously active)
        churned_clients = Client.query.filter(Client.status == 'inactive').count()
        
        # Churn rate
        churn_rate = (churned_clients / total_clients * 100) if total_clients > 0 else 0
        
        # Retention rate
        retention_rate = (total_active / total_clients * 100) if total_clients > 0 else 0
        
        # Clients by status
        clients_by_status = db.session.query(
            Client.status,
            func.count(Client.id).label('count')
        ).group_by(Client.status).all()
        
        status_breakdown = {item[0]: item[1] for item in clients_by_status}
        
        # Client growth trend (monthly)
        monthly_growth = db.session.query(
            extract('year', Client.created_at).label('year'),
            extract('month', Client.created_at).label('month'),
            func.count(Client.id).label('count')
        ).filter(
            Client.created_at >= start_date_year
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        growth_trend = [
            {
                'month': f"{int(item[0])}-{int(item[1]):02d}",
                'new_clients': item[2]
            }
            for item in monthly_growth
        ]
        
        return jsonify({
            'total_clients': total_clients,
            'active_clients': total_active,
            'new_this_month': new_this_month,
            'churned_clients': churned_clients,
            'churn_rate': round(churn_rate, 2),
            'retention_rate': round(retention_rate, 2),
            'status_breakdown': status_breakdown,
            'growth_trend': growth_trend
        }), 200
    except Exception as e:
        logger.error(f"Error calculating client retention: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/clients/engagement', methods=['GET'])
def get_client_engagement():
    """Calculate client engagement metrics"""
    try:
        # Get date range
        end_date = datetime.utcnow()
        start_date_month = end_date - timedelta(days=30)
        
        # Total sessions this month
        total_sessions = Session.query.filter(
            Session.session_date >= start_date_month,
            Session.status == 'completed'
        ).count()
        
        # Average sessions per client
        active_clients = Client.query.filter(Client.status == 'active').count()
        avg_sessions_per_client = total_sessions / active_clients if active_clients > 0 else 0
        
        # Session attendance rate
        scheduled_sessions = Session.query.filter(
            Session.session_date >= start_date_month
        ).count()
        completed_sessions = Session.query.filter(
            Session.session_date >= start_date_month,
            Session.status == 'completed'
        ).count()
        attendance_rate = (completed_sessions / scheduled_sessions * 100) if scheduled_sessions > 0 else 0
        
        # No-show rate
        no_show_sessions = Session.query.filter(
            Session.session_date >= start_date_month,
            Session.status == 'no-show'
        ).count()
        no_show_rate = (no_show_sessions / scheduled_sessions * 100) if scheduled_sessions > 0 else 0
        
        # Clients by activity level (based on sessions this month)
        client_activity = db.session.query(
            Session.client_id,
            func.count(Session.id).label('session_count')
        ).filter(
            Session.session_date >= start_date_month,
            Session.status == 'completed'
        ).group_by(Session.client_id).all()
        
        highly_active = len([c for c in client_activity if c[1] >= 8])  # 2+ per week
        moderately_active = len([c for c in client_activity if 4 <= c[1] < 8])  # 1-2 per week
        low_active = len([c for c in client_activity if 0 < c[1] < 4])  # Less than weekly
        inactive = active_clients - len(client_activity)
        
        # Workout completion rate
        total_workout_logs = WorkoutLog.query.filter(
            WorkoutLog.completed_date >= start_date_month
        ).count()
        
        return jsonify({
            'total_sessions': total_sessions,
            'avg_sessions_per_client': round(avg_sessions_per_client, 2),
            'attendance_rate': round(attendance_rate, 2),
            'no_show_rate': round(no_show_rate, 2),
            'activity_levels': {
                'highly_active': highly_active,
                'moderately_active': moderately_active,
                'low_active': low_active,
                'inactive': inactive
            },
            'workout_logs_completed': total_workout_logs
        }), 200
    except Exception as e:
        logger.error(f"Error calculating client engagement: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/clients/lifetime-value', methods=['GET'])
def get_client_lifetime_value():
    """Calculate client lifetime value (LTV)"""
    try:
        # Get all clients with their payment totals
        client_values = db.session.query(
            Client.id,
            Client.name,
            Client.created_at,
            Client.status,
            func.coalesce(func.sum(Payment.amount), 0).label('total_paid')
        ).outerjoin(
            Payment, (Payment.client_id == Client.id) & (Payment.status == 'completed')
        ).group_by(Client.id).all()
        
        # Calculate metrics
        total_clients = len(client_values)
        total_revenue = sum([float(c[4]) for c in client_values])
        avg_ltv = total_revenue / total_clients if total_clients > 0 else 0
        
        # Calculate average client lifespan (in days)
        # Only count active clients for lifespan calculation
        active_clients_with_dates = [c for c in client_values if c[3] == 'active' and c[2]]
        if active_clients_with_dates:
            total_days = sum((datetime.utcnow() - c[2]).days for c in active_clients_with_dates)
            avg_lifespan_days = total_days / len(active_clients_with_dates)
        else:
            avg_lifespan_days = 0
        
        # Top 10 clients by LTV
        top_clients = sorted(client_values, key=lambda x: float(x[4]), reverse=True)[:10]
        top_clients_list = [
            {
                'client_id': c[0],
                'client_name': c[1],
                'lifetime_value': float(c[4]),
                'status': c[3],
                'member_since': c[2].isoformat() if c[2] else None
            }
            for c in top_clients
        ]
        
        # LTV by membership type - build mapping from client_id to membership and LTV
        # First, get membership types for all clients
        clients_with_membership = Client.query.all()
        client_membership_map = {c.id: c.membership_type for c in clients_with_membership}
        
        # Group LTVs by membership type
        client_ltv_by_membership = {}
        for c in client_values:
            # c = (id, name, created_at, status, total_paid)
            client_id = c[0]
            total_paid = float(c[4])
            membership_type = client_membership_map.get(client_id) or 'None'
            
            if membership_type not in client_ltv_by_membership:
                client_ltv_by_membership[membership_type] = []
            client_ltv_by_membership[membership_type].append(total_paid)
        
        # Calculate averages
        membership_breakdown = []
        for membership_type, ltvs in client_ltv_by_membership.items():
            membership_breakdown.append({
                'membership_type': membership_type,
                'client_count': len(ltvs),
                'average_ltv': sum(ltvs) / len(ltvs) if ltvs else 0
            })
        
        return jsonify({
            'total_clients': total_clients,
            'total_revenue': float(total_revenue),
            'average_ltv': float(avg_ltv),
            'avg_lifespan_days': round(avg_lifespan_days, 0),
            'top_clients': top_clients_list,
            'ltv_by_membership': membership_breakdown
        }), 200
    except Exception as e:
        logger.error(f"Error calculating client lifetime value: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/clients/cohort', methods=['GET'])
def get_cohort_analysis():
    """Perform cohort analysis on clients"""
    try:
        # Get cohort month from query params (default to last 12 months)
        months = request.args.get('months', 12, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get clients grouped by signup month
        cohorts = db.session.query(
            extract('year', Client.created_at).label('year'),
            extract('month', Client.created_at).label('month'),
            func.count(Client.id).label('count')
        ).filter(
            Client.created_at >= start_date
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        cohort_data = []
        for year, month, count in cohorts:
            cohort_start = datetime(int(year), int(month), 1)
            cohort_label = f"{int(year)}-{int(month):02d}"
            
            # Count active clients from this cohort
            active_count = Client.query.filter(
                extract('year', Client.created_at) == year,
                extract('month', Client.created_at) == month,
                Client.status == 'active'
            ).count()
            
            retention = (active_count / count * 100) if count > 0 else 0
            
            cohort_data.append({
                'cohort': cohort_label,
                'initial_size': count,
                'active_count': active_count,
                'retention_rate': round(retention, 2)
            })
        
        return jsonify({
            'cohorts': cohort_data,
            'analysis_period_months': months
        }), 200
    except Exception as e:
        logger.error(f"Error performing cohort analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Trainer Performance Analytics

@analytics_bp.route('/trainers/performance', methods=['GET'])
def get_trainer_performance():
    """Get trainer performance metrics"""
    try:
        # Get date range
        end_date = datetime.utcnow()
        start_date = request.args.get('start_date')
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get all trainers with their metrics
        trainers = Trainer.query.filter(Trainer.active == True).all()
        
        performance_data = []
        for trainer in trainers:
            # Sessions count
            sessions_count = Session.query.filter(
                Session.trainer_id == trainer.id,
                Session.session_date >= start_date,
                Session.status == 'completed'
            ).count()
            
            # Total hours
            total_duration = db.session.query(func.sum(Session.duration)).filter(
                Session.trainer_id == trainer.id,
                Session.session_date >= start_date,
                Session.status == 'completed'
            ).scalar() or 0
            total_hours = total_duration / 60
            
            # Revenue generated
            revenue = db.session.query(func.sum(Payment.amount)).join(
                Client, Payment.client_id == Client.id
            ).join(
                Assignment, Assignment.client_id == Client.id
            ).filter(
                Assignment.trainer_id == trainer.id,
                Payment.status == 'completed',
                Payment.payment_date >= start_date
            ).scalar() or 0
            
            # Active clients
            active_clients = Assignment.query.filter(
                Assignment.trainer_id == trainer.id,
                Assignment.status == 'active'
            ).count()
            
            # Utilization rate (assuming 40 hours per week)
            work_weeks = (end_date - start_date).days / 7
            available_hours = work_weeks * 40
            utilization_rate = (total_hours / available_hours * 100) if available_hours > 0 else 0
            
            performance_data.append({
                'trainer_id': trainer.id,
                'trainer_name': trainer.name,
                'sessions_completed': sessions_count,
                'total_hours': round(total_hours, 2),
                'revenue_generated': float(revenue),
                'active_clients': active_clients,
                'utilization_rate': round(utilization_rate, 2),
                'avg_revenue_per_session': round(float(revenue) / sessions_count, 2) if sessions_count > 0 else 0
            })
        
        # Sort by revenue
        performance_data.sort(key=lambda x: x['revenue_generated'], reverse=True)
        
        return jsonify({
            'trainers': performance_data,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }), 200
    except Exception as e:
        logger.error(f"Error calculating trainer performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/trainers/<int:trainer_id>/performance', methods=['GET'])
def get_single_trainer_performance(trainer_id):
    """Get detailed performance metrics for a specific trainer"""
    trainer = Trainer.query.get_or_404(trainer_id)
    
    try:
        # Get date range
        end_date = datetime.utcnow()
        start_date = request.args.get('start_date')
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Sessions metrics
        total_sessions = Session.query.filter(
            Session.trainer_id == trainer_id,
            Session.session_date >= start_date
        ).count()
        
        completed_sessions = Session.query.filter(
            Session.trainer_id == trainer_id,
            Session.session_date >= start_date,
            Session.status == 'completed'
        ).count()
        
        cancelled_sessions = Session.query.filter(
            Session.trainer_id == trainer_id,
            Session.session_date >= start_date,
            Session.status == 'cancelled'
        ).count()
        
        no_show_sessions = Session.query.filter(
            Session.trainer_id == trainer_id,
            Session.session_date >= start_date,
            Session.status == 'no-show'
        ).count()
        
        completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Revenue metrics
        revenue = db.session.query(func.sum(Payment.amount)).join(
            Client, Payment.client_id == Client.id
        ).join(
            Assignment, Assignment.client_id == Client.id
        ).filter(
            Assignment.trainer_id == trainer_id,
            Payment.status == 'completed',
            Payment.payment_date >= start_date
        ).scalar() or 0
        
        # Client metrics
        total_clients = Assignment.query.filter(
            Assignment.trainer_id == trainer_id
        ).count()
        
        active_clients = Assignment.query.filter(
            Assignment.trainer_id == trainer_id,
            Assignment.status == 'active'
        ).count()
        
        # Session type breakdown
        session_types = db.session.query(
            Session.session_type,
            func.count(Session.id).label('count')
        ).filter(
            Session.trainer_id == trainer_id,
            Session.session_date >= start_date,
            Session.status == 'completed'
        ).group_by(Session.session_type).all()
        
        session_type_breakdown = {item[0] or 'Not specified': item[1] for item in session_types}
        
        # Monthly trend
        monthly_sessions = db.session.query(
            extract('year', Session.session_date).label('year'),
            extract('month', Session.session_date).label('month'),
            func.count(Session.id).label('count')
        ).filter(
            Session.trainer_id == trainer_id,
            Session.session_date >= start_date,
            Session.status == 'completed'
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        monthly_trend = [
            {
                'month': f"{int(item[0])}-{int(item[1]):02d}",
                'sessions': item[2]
            }
            for item in monthly_sessions
        ]
        
        return jsonify({
            'trainer_id': trainer_id,
            'trainer_name': trainer.name,
            'sessions': {
                'total': total_sessions,
                'completed': completed_sessions,
                'cancelled': cancelled_sessions,
                'no_show': no_show_sessions,
                'completion_rate': round(completion_rate, 2)
            },
            'revenue': {
                'total': float(revenue),
                'per_session': round(float(revenue) / completed_sessions, 2) if completed_sessions > 0 else 0
            },
            'clients': {
                'total': total_clients,
                'active': active_clients
            },
            'session_type_breakdown': session_type_breakdown,
            'monthly_trend': monthly_trend,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting trainer performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/trainers/comparison', methods=['GET'])
def get_trainer_comparison():
    """Compare performance metrics across all trainers"""
    try:
        # Get date range
        end_date = datetime.utcnow()
        start_date_month = end_date - timedelta(days=30)
        
        # Get metrics for each trainer
        trainers = Trainer.query.filter(Trainer.active == True).all()
        
        comparison_data = []
        for trainer in trainers:
            sessions = Session.query.filter(
                Session.trainer_id == trainer.id,
                Session.session_date >= start_date_month,
                Session.status == 'completed'
            ).count()
            
            clients = Assignment.query.filter(
                Assignment.trainer_id == trainer.id,
                Assignment.status == 'active'
            ).count()
            
            revenue = db.session.query(func.sum(Payment.amount)).join(
                Client, Payment.client_id == Client.id
            ).join(
                Assignment, Assignment.client_id == Client.id
            ).filter(
                Assignment.trainer_id == trainer.id,
                Payment.status == 'completed',
                Payment.payment_date >= start_date_month
            ).scalar() or 0
            
            comparison_data.append({
                'trainer_id': trainer.id,
                'trainer_name': trainer.name,
                'sessions': sessions,
                'clients': clients,
                'revenue': float(revenue)
            })
        
        # Calculate averages
        avg_sessions = sum([t['sessions'] for t in comparison_data]) / len(comparison_data) if comparison_data else 0
        avg_clients = sum([t['clients'] for t in comparison_data]) / len(comparison_data) if comparison_data else 0
        avg_revenue = sum([t['revenue'] for t in comparison_data]) / len(comparison_data) if comparison_data else 0
        
        return jsonify({
            'trainers': comparison_data,
            'averages': {
                'sessions': round(avg_sessions, 2),
                'clients': round(avg_clients, 2),
                'revenue': round(avg_revenue, 2)
            }
        }), 200
    except Exception as e:
        logger.error(f"Error comparing trainers: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Overall Dashboard Analytics

@analytics_bp.route('/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """Get comprehensive analytics dashboard"""
    try:
        # Get date ranges
        end_date = datetime.utcnow()
        start_date_month = end_date - timedelta(days=30)
        start_date_year = end_date - timedelta(days=365)
        
        # Client metrics
        total_clients = Client.query.count()
        active_clients = Client.query.filter(Client.status == 'active').count()
        new_clients_month = Client.query.filter(Client.created_at >= start_date_month).count()
        
        # Revenue metrics
        total_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        ).scalar() or 0
        
        revenue_month = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.payment_date >= start_date_month
        ).scalar() or 0
        
        # Session metrics
        total_sessions = Session.query.filter(
            Session.session_date >= start_date_month
        ).count()
        
        completed_sessions = Session.query.filter(
            Session.session_date >= start_date_month,
            Session.status == 'completed'
        ).count()
        
        attendance_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Trainer metrics
        active_trainers = Trainer.query.filter(Trainer.active == True).count()
        
        return jsonify({
            'clients': {
                'total': total_clients,
                'active': active_clients,
                'new_this_month': new_clients_month,
                'retention_rate': round((active_clients / total_clients * 100) if total_clients > 0 else 0, 2)
            },
            'revenue': {
                'total': float(total_revenue),
                'this_month': float(revenue_month)
            },
            'sessions': {
                'total': total_sessions,
                'completed': completed_sessions,
                'attendance_rate': round(attendance_rate, 2)
            },
            'trainers': {
                'active': active_trainers
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500
