from flask import Blueprint, request, jsonify
from models.database import db, Goal, GoalMilestone, Client
from datetime import datetime

goal_bp = Blueprint('goals', __name__, url_prefix='/api')

@goal_bp.route('/goals', methods=['GET'])
def get_goals():
    """Get all goals with optional filtering"""
    try:
        query = Goal.query
        
        # Filter by client_id
        client_id = request.args.get('client_id', type=int)
        if client_id:
            query = query.filter_by(client_id=client_id)
        
        # Filter by status
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        # Filter by category
        category = request.args.get('category')
        if category:
            query = query.filter_by(category=category)
        
        # Filter by priority
        priority = request.args.get('priority')
        if priority:
            query = query.filter_by(priority=priority)
        
        # Order by priority and target date
        query = query.order_by(
            db.case(
                (Goal.priority == 'high', 1),
                (Goal.priority == 'medium', 2),
                (Goal.priority == 'low', 3),
                else_=4
            ),
            Goal.target_date.asc()
        )
        
        goals = query.all()
        
        return jsonify({
            'success': True,
            'data': [goal.to_dict() for goal in goals],
            'count': len(goals)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@goal_bp.route('/goals/<int:id>', methods=['GET'])
def get_goal(id):
    """Get a specific goal"""
    try:
        goal = Goal.query.get_or_404(id)
        return jsonify({
            'success': True,
            'data': goal.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@goal_bp.route('/goals', methods=['POST'])
def create_goal():
    """Create a new goal"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('client_id'):
            return jsonify({'success': False, 'error': 'client_id is required'}), 400
        if not data.get('title'):
            return jsonify({'success': False, 'error': 'title is required'}), 400
        
        # Verify client exists
        client = Client.query.get(data['client_id'])
        if not client:
            return jsonify({'success': False, 'error': 'Client not found'}), 404
        
        goal = Goal(
            client_id=data['client_id'],
            title=data['title'],
            description=data.get('description'),
            category=data.get('category', 'other'),
            target_value=data.get('target_value'),
            target_unit=data.get('target_unit'),
            current_value=data.get('current_value', 0),
            target_date=datetime.fromisoformat(data['target_date']) if data.get('target_date') else None,
            status=data.get('status', 'active'),
            priority=data.get('priority', 'medium'),
            notes=data.get('notes'),
            created_by=data.get('created_by')
        )
        
        db.session.add(goal)
        db.session.commit()
        
        # Add milestones if provided
        if data.get('milestones'):
            for milestone_data in data['milestones']:
                milestone = GoalMilestone(
                    goal_id=goal.id,
                    title=milestone_data['title'],
                    description=milestone_data.get('description'),
                    target_value=milestone_data.get('target_value'),
                    target_date=datetime.fromisoformat(milestone_data['target_date']) if milestone_data.get('target_date') else None
                )
                db.session.add(milestone)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Goal created successfully',
            'data': goal.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@goal_bp.route('/goals/<int:id>', methods=['PUT'])
def update_goal(id):
    """Update a goal"""
    try:
        goal = Goal.query.get_or_404(id)
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            goal.title = data['title']
        if 'description' in data:
            goal.description = data['description']
        if 'category' in data:
            goal.category = data['category']
        if 'target_value' in data:
            goal.target_value = data['target_value']
        if 'target_unit' in data:
            goal.target_unit = data['target_unit']
        if 'current_value' in data:
            goal.current_value = data['current_value']
            # Check if goal is completed
            if goal.target_value and goal.current_value >= goal.target_value and goal.status == 'active':
                goal.status = 'completed'
                goal.completed_date = datetime.utcnow()
        if 'target_date' in data:
            goal.target_date = datetime.fromisoformat(data['target_date']) if data['target_date'] else None
        if 'status' in data:
            goal.status = data['status']
            if data['status'] == 'completed' and not goal.completed_date:
                goal.completed_date = datetime.utcnow()
        if 'priority' in data:
            goal.priority = data['priority']
        if 'notes' in data:
            goal.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Goal updated successfully',
            'data': goal.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@goal_bp.route('/goals/<int:id>', methods=['DELETE'])
def delete_goal(id):
    """Delete a goal"""
    try:
        goal = Goal.query.get_or_404(id)
        db.session.delete(goal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Goal deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@goal_bp.route('/goals/<int:goal_id>/milestones', methods=['POST'])
def create_milestone(goal_id):
    """Create a new milestone for a goal"""
    try:
        goal = Goal.query.get_or_404(goal_id)
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({'success': False, 'error': 'title is required'}), 400
        
        milestone = GoalMilestone(
            goal_id=goal_id,
            title=data['title'],
            description=data.get('description'),
            target_value=data.get('target_value'),
            target_date=datetime.fromisoformat(data['target_date']) if data.get('target_date') else None
        )
        
        db.session.add(milestone)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Milestone created successfully',
            'data': milestone.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@goal_bp.route('/goals/<int:goal_id>/milestones/<int:milestone_id>', methods=['PUT'])
def update_milestone(goal_id, milestone_id):
    """Update a milestone"""
    try:
        milestone = GoalMilestone.query.filter_by(id=milestone_id, goal_id=goal_id).first_or_404()
        data = request.get_json()
        
        if 'title' in data:
            milestone.title = data['title']
        if 'description' in data:
            milestone.description = data['description']
        if 'target_value' in data:
            milestone.target_value = data['target_value']
        if 'target_date' in data:
            milestone.target_date = datetime.fromisoformat(data['target_date']) if data['target_date'] else None
        if 'completed' in data:
            milestone.completed = data['completed']
            if data['completed'] and not milestone.completed_date:
                milestone.completed_date = datetime.utcnow()
            elif not data['completed']:
                milestone.completed_date = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Milestone updated successfully',
            'data': milestone.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@goal_bp.route('/goals/<int:goal_id>/milestones/<int:milestone_id>', methods=['DELETE'])
def delete_milestone(goal_id, milestone_id):
    """Delete a milestone"""
    try:
        milestone = GoalMilestone.query.filter_by(id=milestone_id, goal_id=goal_id).first_or_404()
        db.session.delete(milestone)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Milestone deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@goal_bp.route('/goals/client/<int:client_id>/summary', methods=['GET'])
def get_client_goals_summary(client_id):
    """Get summary of client's goals"""
    try:
        goals = Goal.query.filter_by(client_id=client_id).all()
        
        summary = {
            'total_goals': len(goals),
            'active_goals': len([g for g in goals if g.status == 'active']),
            'completed_goals': len([g for g in goals if g.status == 'completed']),
            'high_priority': len([g for g in goals if g.priority == 'high' and g.status == 'active']),
            'goals': [goal.to_dict() for goal in goals]
        }
        
        return jsonify({
            'success': True,
            'data': summary
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
