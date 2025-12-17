from flask import Blueprint, request, jsonify
from models.database import db, Payment, Client
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from utils.logger import log_activity, logger

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payments')

# Payment CRUD Operations

@payment_bp.route('', methods=['GET'])
def get_payments():
    """Get all payments with optional filters"""
    query = Payment.query
    
    # Filter by client
    client_id = request.args.get('client_id', type=int)
    if client_id:
        query = query.filter(Payment.client_id == client_id)
    
    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter(Payment.status == status)
    
    # Filter by payment type
    payment_type = request.args.get('payment_type')
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    
    # Filter by date range
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date:
        query = query.filter(Payment.payment_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Payment.payment_date <= datetime.fromisoformat(end_date))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    per_page = min(per_page, 100)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    query = query.order_by(Payment.payment_date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get client names
    payments = []
    for payment in pagination.items:
        payment_dict = payment.to_dict()
        client = Client.query.get(payment.client_id)
        payment_dict['client_name'] = client.name if client else 'Unknown'
        payments.append(payment_dict)
    
    return jsonify({
        'items': payments,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }), 200

@payment_bp.route('/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """Get a specific payment"""
    payment = Payment.query.get_or_404(payment_id)
    payment_dict = payment.to_dict()
    
    # Add client information
    client = Client.query.get(payment.client_id)
    payment_dict['client_name'] = client.name if client else 'Unknown'
    
    return jsonify(payment_dict), 200

@payment_bp.route('', methods=['POST'])
def create_payment():
    """Create a new payment"""
    data = request.get_json()
    
    if not data or not data.get('client_id') or not data.get('amount'):
        return jsonify({'error': 'Client ID and amount are required'}), 400
    
    # Validate client exists
    client = Client.query.get(data.get('client_id'))
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    try:
        payment = Payment(
            client_id=data['client_id'],
            amount=data['amount'],
            payment_date=datetime.fromisoformat(data['payment_date']) if data.get('payment_date') else datetime.utcnow(),
            payment_method=data.get('payment_method', 'credit_card'),
            payment_type=data.get('payment_type', 'membership'),
            status=data.get('status', 'completed'),
            transaction_id=data.get('transaction_id'),
            notes=data.get('notes')
        )
        db.session.add(payment)
        db.session.commit()
        
        log_activity('create', 'payment', payment.id, user_identifier='system',
                    details={'client_id': payment.client_id, 'amount': payment.amount})
        logger.info(f"Payment created: ${payment.amount} for client {client.name} (ID: {payment.id})")
        
        payment_dict = payment.to_dict()
        payment_dict['client_name'] = client.name
        
        return jsonify(payment_dict), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating payment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    """Update a payment"""
    payment = Payment.query.get_or_404(payment_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Update fields
        if 'amount' in data:
            payment.amount = data['amount']
        if 'payment_date' in data:
            payment.payment_date = datetime.fromisoformat(data['payment_date'])
        if 'payment_method' in data:
            payment.payment_method = data['payment_method']
        if 'payment_type' in data:
            payment.payment_type = data['payment_type']
        if 'status' in data:
            payment.status = data['status']
        if 'transaction_id' in data:
            payment.transaction_id = data['transaction_id']
        if 'notes' in data:
            payment.notes = data['notes']
        
        db.session.commit()
        
        log_activity('update', 'payment', payment.id, user_identifier='system',
                    details={'amount': payment.amount})
        logger.info(f"Payment updated: ID {payment.id}")
        
        payment_dict = payment.to_dict()
        client = Client.query.get(payment.client_id)
        payment_dict['client_name'] = client.name if client else 'Unknown'
        
        return jsonify(payment_dict), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating payment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    """Delete a payment"""
    payment = Payment.query.get_or_404(payment_id)
    
    try:
        log_activity('delete', 'payment', payment.id, user_identifier='system',
                    details={'amount': payment.amount, 'client_id': payment.client_id})
        
        db.session.delete(payment)
        db.session.commit()
        
        logger.info(f"Payment deleted: ID {payment_id}")
        return jsonify({'message': 'Payment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting payment: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Revenue Analytics Endpoints

@payment_bp.route('/revenue/dashboard', methods=['GET'])
def get_revenue_dashboard():
    """Get revenue dashboard with key metrics"""
    try:
        # Get date range
        end_date = datetime.utcnow()
        start_date_month = end_date - timedelta(days=30)
        start_date_year = end_date - timedelta(days=365)
        
        # Total revenue (all time)
        total_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        ).scalar() or 0
        
        # Revenue this month
        revenue_this_month = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.payment_date >= start_date_month
        ).scalar() or 0
        
        # Revenue this year
        revenue_this_year = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.payment_date >= start_date_year
        ).scalar() or 0
        
        # Total payments count
        total_payments = Payment.query.filter(Payment.status == 'completed').count()
        
        # Pending payments
        pending_amount = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'pending'
        ).scalar() or 0
        
        pending_count = Payment.query.filter(Payment.status == 'pending').count()
        
        # Average payment amount
        avg_payment = db.session.query(func.avg(Payment.amount)).filter(
            Payment.status == 'completed'
        ).scalar() or 0
        
        # Revenue by payment type
        revenue_by_type = db.session.query(
            Payment.payment_type,
            func.sum(Payment.amount).label('total')
        ).filter(
            Payment.status == 'completed'
        ).group_by(Payment.payment_type).all()
        
        revenue_by_type_dict = {item[0]: float(item[1]) for item in revenue_by_type}
        
        # Monthly revenue trend (last 12 months)
        monthly_revenue = db.session.query(
            extract('year', Payment.payment_date).label('year'),
            extract('month', Payment.payment_date).label('month'),
            func.sum(Payment.amount).label('total')
        ).filter(
            Payment.status == 'completed',
            Payment.payment_date >= start_date_year
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        monthly_trend = [
            {
                'month': f"{int(item[0])}-{int(item[1]):02d}",
                'revenue': float(item[2])
            }
            for item in monthly_revenue
        ]
        
        return jsonify({
            'total_revenue': float(total_revenue),
            'revenue_this_month': float(revenue_this_month),
            'revenue_this_year': float(revenue_this_year),
            'total_payments': total_payments,
            'pending_amount': float(pending_amount),
            'pending_count': pending_count,
            'average_payment': float(avg_payment),
            'revenue_by_type': revenue_by_type_dict,
            'monthly_trend': monthly_trend
        }), 200
    except Exception as e:
        logger.error(f"Error getting revenue dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/revenue/report', methods=['GET'])
def get_revenue_report():
    """Get detailed revenue report with custom date range"""
    try:
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Payment.query.filter(Payment.status == 'completed')
        
        if start_date:
            query = query.filter(Payment.payment_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Payment.payment_date <= datetime.fromisoformat(end_date))
        
        # Total revenue
        total = db.session.query(func.sum(Payment.amount)).filter(
            query.whereclause if hasattr(query, 'whereclause') else True
        ).scalar() or 0
        
        # Payment count
        count = query.count()
        
        # Average payment
        average = total / count if count > 0 else 0
        
        # Revenue by payment method
        revenue_by_method = db.session.query(
            Payment.payment_method,
            func.sum(Payment.amount).label('total'),
            func.count(Payment.id).label('count')
        ).filter(
            Payment.status == 'completed'
        )
        
        if start_date:
            revenue_by_method = revenue_by_method.filter(Payment.payment_date >= datetime.fromisoformat(start_date))
        if end_date:
            revenue_by_method = revenue_by_method.filter(Payment.payment_date <= datetime.fromisoformat(end_date))
        
        revenue_by_method = revenue_by_method.group_by(Payment.payment_method).all()
        
        method_breakdown = [
            {
                'method': item[0],
                'total': float(item[1]),
                'count': item[2]
            }
            for item in revenue_by_method
        ]
        
        # Revenue by payment type
        revenue_by_type = db.session.query(
            Payment.payment_type,
            func.sum(Payment.amount).label('total'),
            func.count(Payment.id).label('count')
        ).filter(
            Payment.status == 'completed'
        )
        
        if start_date:
            revenue_by_type = revenue_by_type.filter(Payment.payment_date >= datetime.fromisoformat(start_date))
        if end_date:
            revenue_by_type = revenue_by_type.filter(Payment.payment_date <= datetime.fromisoformat(end_date))
        
        revenue_by_type = revenue_by_type.group_by(Payment.payment_type).all()
        
        type_breakdown = [
            {
                'type': item[0],
                'total': float(item[1]),
                'count': item[2]
            }
            for item in revenue_by_type
        ]
        
        # Top paying clients
        top_clients = db.session.query(
            Payment.client_id,
            func.sum(Payment.amount).label('total')
        ).filter(
            Payment.status == 'completed'
        )
        
        if start_date:
            top_clients = top_clients.filter(Payment.payment_date >= datetime.fromisoformat(start_date))
        if end_date:
            top_clients = top_clients.filter(Payment.payment_date <= datetime.fromisoformat(end_date))
        
        top_clients = top_clients.group_by(Payment.client_id).order_by(func.sum(Payment.amount).desc()).limit(10).all()
        
        top_clients_list = []
        for client_id, total in top_clients:
            client = Client.query.get(client_id)
            if client:
                top_clients_list.append({
                    'client_id': client_id,
                    'client_name': client.name,
                    'total': float(total)
                })
        
        return jsonify({
            'total_revenue': float(total),
            'payment_count': count,
            'average_payment': float(average),
            'revenue_by_method': method_breakdown,
            'revenue_by_type': type_breakdown,
            'top_clients': top_clients_list,
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }), 200
    except Exception as e:
        logger.error(f"Error generating revenue report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/client/<int:client_id>/summary', methods=['GET'])
def get_client_payment_summary(client_id):
    """Get payment summary for a specific client"""
    client = Client.query.get_or_404(client_id)
    
    try:
        # Total paid
        total_paid = db.session.query(func.sum(Payment.amount)).filter(
            Payment.client_id == client_id,
            Payment.status == 'completed'
        ).scalar() or 0
        
        # Total pending
        total_pending = db.session.query(func.sum(Payment.amount)).filter(
            Payment.client_id == client_id,
            Payment.status == 'pending'
        ).scalar() or 0
        
        # Payment count
        payment_count = Payment.query.filter(
            Payment.client_id == client_id,
            Payment.status == 'completed'
        ).count()
        
        # Last payment date
        last_payment = Payment.query.filter(
            Payment.client_id == client_id,
            Payment.status == 'completed'
        ).order_by(Payment.payment_date.desc()).first()
        
        return jsonify({
            'client_id': client_id,
            'client_name': client.name,
            'total_paid': float(total_paid),
            'total_pending': float(total_pending),
            'payment_count': payment_count,
            'last_payment_date': last_payment.payment_date.isoformat() if last_payment else None,
            'last_payment_amount': float(last_payment.amount) if last_payment else None
        }), 200
    except Exception as e:
        logger.error(f"Error getting client payment summary: {str(e)}")
        return jsonify({'error': str(e)}), 500
