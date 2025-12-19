"""
Unit tests for goal API routes.
"""

import pytest
from datetime import datetime, timedelta
from models.database import Goal, GoalMilestone, Client


class TestGoalRoutes:
    """Test goal API endpoints."""
    
    @pytest.mark.api
    def test_get_goals(self, client):
        """Test GET /api/goals returns goal list."""
        response = client.get('/api/goals')
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'success' in data
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    @pytest.mark.api
    def test_create_goal(self, client, db_session, sample_client):
        """Test POST /api/goals creates a goal."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        goal_data = {
            'client_id': client_obj.id,
            'title': 'Lose 10 pounds',
            'description': 'Weight loss goal',
            'category': 'weight_loss',
            'target_value': '10',
            'target_date': (datetime.now() + timedelta(days=90)).isoformat(),
            'priority': 'high',
            'status': 'active'
        }
        response = client.post('/api/goals', json=goal_data)
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'data' in data
        goal = data['data']
        assert goal['title'] == 'Lose 10 pounds'
        assert goal['client_id'] == client_obj.id
    
    @pytest.mark.api
    def test_create_goal_missing_client_id(self, client):
        """Test POST /api/goals without client_id."""
        goal_data = {
            'title': 'Test Goal'
        }
        response = client.post('/api/goals', json=goal_data)
        assert response.status_code == 400
    
    @pytest.mark.api
    def test_create_goal_missing_title(self, client, db_session, sample_client):
        """Test POST /api/goals without title."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        goal_data = {
            'client_id': client_obj.id,
            'description': 'Goal without title'
        }
        response = client.post('/api/goals', json=goal_data)
        assert response.status_code == 400
    
    @pytest.mark.api
    def test_get_goal_by_id(self, client, db_session, sample_client):
        """Test GET /api/goals/<id> returns specific goal."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        goal = Goal(
            client_id=client_obj.id,
            title='Build Muscle',
            category='muscle_gain',
            target_date=datetime.now() + timedelta(days=60),
            status='active'
        )
        db_session.add(goal)
        db_session.commit()
        
        response = client.get(f'/api/goals/{goal.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['id'] == goal.id
        assert data['data']['title'] == 'Build Muscle'
    
    @pytest.mark.api
    def test_update_goal(self, client, db_session, sample_client):
        """Test PUT /api/goals/<id> updates goal."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        goal = Goal(
            client_id=client_obj.id,
            title='Run 5K',
            category='endurance',
            status='active'
        )
        db_session.add(goal)
        db_session.commit()
        
        update_data = {
            'status': 'completed',
            'progress_percentage': 100,
            'notes': 'Goal achieved!'
        }
        response = client.put(f'/api/goals/{goal.id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['status'] == 'completed'
        assert data['data']['progress_percentage'] == 100
    
    @pytest.mark.api
    def test_delete_goal(self, client, db_session, sample_client):
        """Test DELETE /api/goals/<id> deletes goal."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        goal = Goal(
            client_id=client_obj.id,
            title='Flexibility Goal',
            category='flexibility',
            status='active'
        )
        db_session.add(goal)
        db_session.commit()
        goal_id = goal.id
        
        response = client.delete(f'/api/goals/{goal_id}')
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f'/api/goals/{goal_id}')
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_filter_goals_by_client(self, client, db_session, sample_client):
        """Test filtering goals by client_id."""
        client1 = Client(**sample_client)
        client2_data = sample_client.copy()
        client2_data['email'] = 'client2@example.com'
        client2 = Client(**client2_data)
        db_session.add_all([client1, client2])
        db_session.commit()
        
        goal1 = Goal(client_id=client1.id, title='Goal 1', category='weight_loss', status='active')
        goal2 = Goal(client_id=client2.id, title='Goal 2', category='muscle_gain', status='active')
        db_session.add_all([goal1, goal2])
        db_session.commit()
        
        response = client.get(f'/api/goals?client_id={client1.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        goals = data['data']
        assert all(g['client_id'] == client1.id for g in goals)
    
    @pytest.mark.api
    def test_filter_goals_by_status(self, client, db_session, sample_client):
        """Test filtering goals by status."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        goal1 = Goal(client_id=client_obj.id, title='Active Goal', category='weight_loss', status='active')
        goal2 = Goal(client_id=client_obj.id, title='Completed Goal', category='muscle_gain', status='completed')
        db_session.add_all([goal1, goal2])
        db_session.commit()
        
        response = client.get('/api/goals?status=active')
        assert response.status_code == 200
        data = response.get_json()
        
        goals = data['data']
        assert all(g['status'] == 'active' for g in goals)
    
    @pytest.mark.api
    def test_filter_goals_by_category(self, client, db_session, sample_client):
        """Test filtering goals by category."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        goal1 = Goal(client_id=client_obj.id, title='Lose Weight', category='weight_loss', status='active')
        goal2 = Goal(client_id=client_obj.id, title='Build Muscle', category='muscle_gain', status='active')
        db_session.add_all([goal1, goal2])
        db_session.commit()
        
        response = client.get('/api/goals?category=weight_loss')
        assert response.status_code == 200
        data = response.get_json()
        
        goals = data['data']
        assert all(g['category'] == 'weight_loss' for g in goals)
    
    @pytest.mark.api
    def test_filter_goals_by_priority(self, client, db_session, sample_client):
        """Test filtering goals by priority."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        goal1 = Goal(client_id=client_obj.id, title='High Priority', category='weight_loss', priority='high', status='active')
        goal2 = Goal(client_id=client_obj.id, title='Low Priority', category='muscle_gain', priority='low', status='active')
        db_session.add_all([goal1, goal2])
        db_session.commit()
        
        response = client.get('/api/goals?priority=high')
        assert response.status_code == 200
        data = response.get_json()
        
        goals = data['data']
        assert all(g['priority'] == 'high' for g in goals)


class TestGoalMilestoneRoutes:
    """Test goal milestone endpoints."""
    
    @pytest.mark.api
    def test_create_milestone(self, client, db_session, sample_client):
        """Test creating a milestone for a goal."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        goal = Goal(
            client_id=client_obj.id,
            title='Marathon Training',
            category='endurance',
            status='active'
        )
        db_session.add(goal)
        db_session.commit()
        
        milestone_data = {
            'goal_id': goal.id,
            'title': 'Run 10K',
            'target_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'status': 'pending'
        }
        
        response = client.post(f'/api/goals/{goal.id}/milestones', json=milestone_data)
        # Accept various success codes
        assert response.status_code in [200, 201]
    
    @pytest.mark.integration
    def test_goal_progress_tracking(self, client, db_session, sample_client):
        """Test tracking goal progress over time."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        goal = Goal(
            client_id=client_obj.id,
            title='Weight Loss Journey',
            category='weight_loss',
            target_value='20',
            current_value='0',
            progress_percentage=0,
            status='active'
        )
        db_session.add(goal)
        db_session.commit()
        
        # Update progress
        update_data = {
            'current_value': '5',
            'progress_percentage': 25
        }
        response = client.put(f'/api/goals/{goal.id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['data']['current_value'] == '5'
        assert data['data']['progress_percentage'] == 25
