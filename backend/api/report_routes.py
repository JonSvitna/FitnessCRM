from flask import Blueprint, request, jsonify, send_file
from models.database import db, Client, Trainer, Session, Payment, Assignment
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import csv
import io
from utils.logger import logger

report_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@report_bp.route('/custom', methods=['POST'])
def generate_custom_report():
    """Generate a custom report based on user-selected metrics and filters"""
    try:
        data = request.get_json()
        
        # Get report parameters
        metrics = data.get('metrics', [])  # List of metrics to include
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        if not metrics:
            return jsonify({'error': 'At least one metric must be selected'}), 400
        
        # Parse dates
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str)
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
        
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str)
        else:
            end_date = datetime.utcnow()
        
        # Use shared function to generate report
        report_data = _generate_report_data(
            data.get('name', 'Custom Report'),
            metrics,
            start_date,
            end_date
        )
        return jsonify(report_data), 200
    except Exception as e:
        logger.error(f"Error generating custom report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@report_bp.route('/custom/export', methods=['POST'])
def export_custom_report():
    """Export custom report to CSV"""
    try:
        data = request.get_json()
        report_data = data.get('report_data')
        
        if not report_data:
            return jsonify({'error': 'Report data is required'}), 400
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Custom Report'])
        writer.writerow(['Generated:', report_data.get('generated_at', '')])
        writer.writerow(['Date Range:', f"{report_data.get('date_range', {}).get('start', '')} to {report_data.get('date_range', {}).get('end', '')}"])
        writer.writerow([])
        
        # Write metrics
        writer.writerow(['Metric', 'Value'])
        metrics = report_data.get('metrics', {})
        
        for key, value in metrics.items():
            if isinstance(value, dict):
                writer.writerow([key, ''])
                for sub_key, sub_value in value.items():
                    writer.writerow([f'  {sub_key}', sub_value])
            elif isinstance(value, list):
                writer.writerow([key, ''])
                for item in value:
                    if isinstance(item, dict):
                        # Format dict items in a readable way
                        formatted_item = ', '.join([f"{k}: {v}" for k, v in item.items()])
                        writer.writerow(['', formatted_item])
                    else:
                        writer.writerow(['', str(item)])
            else:
                writer.writerow([key.replace('_', ' ').title(), value])
        
        # Prepare the response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"custom_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    except Exception as e:
        logger.error(f"Error exporting custom report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@report_bp.route('/templates', methods=['GET'])
def get_report_templates():
    """Get predefined report templates"""
    templates = [
        {
            'id': 'monthly_revenue',
            'name': 'Monthly Revenue Report',
            'description': 'Comprehensive revenue breakdown for the month',
            'metrics': ['total_revenue', 'payment_count', 'revenue_by_type'],
            'default_date_range': 'last_30_days'
        },
        {
            'id': 'client_growth',
            'name': 'Client Growth Report',
            'description': 'Track client acquisition and retention',
            'metrics': ['client_count', 'active_clients', 'new_clients'],
            'default_date_range': 'last_90_days'
        },
        {
            'id': 'session_performance',
            'name': 'Session Performance Report',
            'description': 'Analysis of session attendance and completion',
            'metrics': ['total_sessions', 'completed_sessions', 'attendance_rate', 'sessions_by_type'],
            'default_date_range': 'last_30_days'
        },
        {
            'id': 'trainer_overview',
            'name': 'Trainer Overview Report',
            'description': 'Performance metrics for all trainers',
            'metrics': ['active_trainers', 'trainer_performance'],
            'default_date_range': 'last_30_days'
        },
        {
            'id': 'comprehensive',
            'name': 'Comprehensive Business Report',
            'description': 'All key metrics in one report',
            'metrics': [
                'total_revenue', 'payment_count', 'client_count', 'active_clients',
                'new_clients', 'total_sessions', 'completed_sessions', 'attendance_rate',
                'active_trainers', 'revenue_by_type', 'sessions_by_type'
            ],
            'default_date_range': 'last_30_days'
        }
    ]
    
    return jsonify({'templates': templates}), 200

def _generate_report_data(name, metrics, start_date, end_date):
    """Shared function to generate report data"""
    # Parse dates
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)
    
    report_data = {
        'report_name': name,
        'generated_at': datetime.utcnow().isoformat(),
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'metrics': {}
    }
    
    # Calculate requested metrics (same logic as in generate_custom_report)
    for metric in metrics:
        if metric == 'total_revenue':
            revenue = db.session.query(func.sum(Payment.amount)).filter(
                Payment.status == 'completed',
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ).scalar() or 0
            report_data['metrics']['total_revenue'] = float(revenue)
        
        elif metric == 'payment_count':
            count = Payment.query.filter(
                Payment.status == 'completed',
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ).count()
            report_data['metrics']['payment_count'] = count
        
        elif metric == 'client_count':
            count = Client.query.filter(
                Client.created_at <= end_date
            ).count()
            report_data['metrics']['client_count'] = count
        
        elif metric == 'active_clients':
            count = Client.query.filter(
                Client.status == 'active',
                Client.created_at <= end_date
            ).count()
            report_data['metrics']['active_clients'] = count
        
        elif metric == 'new_clients':
            count = Client.query.filter(
                Client.created_at >= start_date,
                Client.created_at <= end_date
            ).count()
            report_data['metrics']['new_clients'] = count
        
        elif metric == 'total_sessions':
            count = Session.query.filter(
                Session.session_date >= start_date,
                Session.session_date <= end_date
            ).count()
            report_data['metrics']['total_sessions'] = count
        
        elif metric == 'completed_sessions':
            count = Session.query.filter(
                Session.session_date >= start_date,
                Session.session_date <= end_date,
                Session.status == 'completed'
            ).count()
            report_data['metrics']['completed_sessions'] = count
        
        elif metric == 'attendance_rate':
            total = Session.query.filter(
                Session.session_date >= start_date,
                Session.session_date <= end_date
            ).count()
            completed = Session.query.filter(
                Session.session_date >= start_date,
                Session.session_date <= end_date,
                Session.status == 'completed'
            ).count()
            rate = (completed / total * 100) if total > 0 else 0
            report_data['metrics']['attendance_rate'] = round(rate, 2)
        
        elif metric == 'active_trainers':
            count = Trainer.query.filter(Trainer.active == True).count()
            report_data['metrics']['active_trainers'] = count
        
        elif metric == 'revenue_by_type':
            revenue_by_type = db.session.query(
                Payment.payment_type,
                func.sum(Payment.amount).label('total')
            ).filter(
                Payment.status == 'completed',
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ).group_by(Payment.payment_type).all()
            
            report_data['metrics']['revenue_by_type'] = {
                item[0] or 'Not specified': float(item[1]) for item in revenue_by_type
            }
        
        elif metric == 'sessions_by_type':
            sessions_by_type = db.session.query(
                Session.session_type,
                func.count(Session.id).label('count')
            ).filter(
                Session.session_date >= start_date,
                Session.session_date <= end_date,
                Session.status == 'completed'
            ).group_by(Session.session_type).all()
            
            report_data['metrics']['sessions_by_type'] = {
                item[0] or 'Not specified': item[1] for item in sessions_by_type
            }
        
        elif metric == 'trainer_performance':
            trainers = Trainer.query.filter(Trainer.active == True).all()
            performance = []
            
            for trainer in trainers:
                sessions = Session.query.filter(
                    Session.trainer_id == trainer.id,
                    Session.session_date >= start_date,
                    Session.session_date <= end_date,
                    Session.status == 'completed'
                ).count()
                
                revenue = db.session.query(func.sum(Payment.amount)).join(
                    Client, Payment.client_id == Client.id
                ).join(
                    Assignment, Assignment.client_id == Client.id
                ).filter(
                    Assignment.trainer_id == trainer.id,
                    Payment.status == 'completed',
                    Payment.payment_date >= start_date,
                    Payment.payment_date <= end_date
                ).scalar() or 0
                
                performance.append({
                    'trainer_name': trainer.name,
                    'sessions': sessions,
                    'revenue': float(revenue)
                })
            
            report_data['metrics']['trainer_performance'] = performance
    
    return report_data

@report_bp.route('/templates/<template_id>', methods=['POST'])
def generate_from_template(template_id):
    """Generate a report from a predefined template"""
    try:
        data = request.get_json() or {}
        
        # Get the template
        templates_response = get_report_templates()
        templates_data = templates_response[0].get_json()
        templates = templates_data.get('templates', [])
        
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Get date range
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date:
            # Apply default date range
            end_date_dt = datetime.utcnow()
            if template['default_date_range'] == 'last_30_days':
                start_date_dt = end_date_dt - timedelta(days=30)
            elif template['default_date_range'] == 'last_90_days':
                start_date_dt = end_date_dt - timedelta(days=90)
            elif template['default_date_range'] == 'last_year':
                start_date_dt = end_date_dt - timedelta(days=365)
            else:
                start_date_dt = end_date_dt - timedelta(days=30)
        else:
            start_date_dt = datetime.fromisoformat(start_date)
            if end_date:
                end_date_dt = datetime.fromisoformat(end_date)
            else:
                end_date_dt = datetime.utcnow()
        
        # Generate the report using shared function
        report_data = _generate_report_data(
            template['name'],
            template['metrics'],
            start_date_dt,
            end_date_dt
        )
        
        return jsonify(report_data), 200
    except Exception as e:
        logger.error(f"Error generating report from template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@report_bp.route('/available-metrics', methods=['GET'])
def get_available_metrics():
    """Get list of all available metrics for custom reports"""
    metrics = [
        {
            'id': 'total_revenue',
            'name': 'Total Revenue',
            'description': 'Sum of all completed payments',
            'category': 'revenue'
        },
        {
            'id': 'payment_count',
            'name': 'Payment Count',
            'description': 'Number of completed payments',
            'category': 'revenue'
        },
        {
            'id': 'revenue_by_type',
            'name': 'Revenue by Type',
            'description': 'Revenue breakdown by payment type',
            'category': 'revenue'
        },
        {
            'id': 'client_count',
            'name': 'Total Clients',
            'description': 'Total number of clients',
            'category': 'clients'
        },
        {
            'id': 'active_clients',
            'name': 'Active Clients',
            'description': 'Number of active clients',
            'category': 'clients'
        },
        {
            'id': 'new_clients',
            'name': 'New Clients',
            'description': 'Clients added in date range',
            'category': 'clients'
        },
        {
            'id': 'total_sessions',
            'name': 'Total Sessions',
            'description': 'All scheduled sessions',
            'category': 'sessions'
        },
        {
            'id': 'completed_sessions',
            'name': 'Completed Sessions',
            'description': 'Successfully completed sessions',
            'category': 'sessions'
        },
        {
            'id': 'attendance_rate',
            'name': 'Attendance Rate',
            'description': 'Percentage of completed sessions',
            'category': 'sessions'
        },
        {
            'id': 'sessions_by_type',
            'name': 'Sessions by Type',
            'description': 'Session breakdown by type',
            'category': 'sessions'
        },
        {
            'id': 'active_trainers',
            'name': 'Active Trainers',
            'description': 'Number of active trainers',
            'category': 'trainers'
        },
        {
            'id': 'trainer_performance',
            'name': 'Trainer Performance',
            'description': 'Sessions and revenue per trainer',
            'category': 'trainers'
        }
    ]
    
    return jsonify({'metrics': metrics}), 200
