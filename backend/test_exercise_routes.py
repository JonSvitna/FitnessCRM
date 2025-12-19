"""
Unit tests for exercise API routes.
"""

import pytest
from models.database import Exercise


class TestExerciseRoutes:
    """Test exercise API endpoints."""
    
    @pytest.mark.api
    def test_get_exercises(self, client):
        """Test GET /api/exercises returns exercise list."""
        response = client.get('/api/exercises')
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'exercises' in data
        assert 'total' in data
        assert isinstance(data['exercises'], list)
    
    @pytest.mark.api
    def test_create_exercise(self, client):
        """Test POST /api/exercises creates an exercise."""
        exercise_data = {
            'name': 'Bench Press',
            'category': 'strength',
            'muscle_group': 'chest',
            'equipment': 'barbell',
            'difficulty': 'intermediate',
            'description': 'Classic chest exercise',
            'instructions': 'Lie on bench, lower bar to chest, press up'
        }
        response = client.post('/api/exercises', json=exercise_data)
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data
        assert data['name'] == 'Bench Press'
        assert data['category'] == 'strength'
    
    @pytest.mark.api
    def test_create_exercise_missing_name(self, client):
        """Test POST /api/exercises without required name field."""
        exercise_data = {
            'category': 'strength',
            'muscle_group': 'chest'
        }
        response = client.post('/api/exercises', json=exercise_data)
        assert response.status_code == 400
    
    @pytest.mark.api
    def test_get_exercise_by_id(self, client, db_session):
        """Test GET /api/exercises/<id> returns specific exercise."""
        exercise = Exercise(
            name='Squats',
            category='strength',
            muscle_group='legs',
            difficulty='intermediate'
        )
        db_session.add(exercise)
        db_session.commit()
        
        response = client.get(f'/api/exercises/{exercise.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['id'] == exercise.id
        assert data['name'] == 'Squats'
    
    @pytest.mark.api
    def test_update_exercise(self, client, db_session):
        """Test PUT /api/exercises/<id> updates exercise."""
        exercise = Exercise(
            name='Push-ups',
            category='bodyweight',
            muscle_group='chest'
        )
        db_session.add(exercise)
        db_session.commit()
        
        update_data = {
            'difficulty': 'beginner',
            'description': 'Basic push-up exercise'
        }
        response = client.put(f'/api/exercises/{exercise.id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['difficulty'] == 'beginner'
        assert data['description'] == 'Basic push-up exercise'
    
    @pytest.mark.api
    def test_delete_exercise(self, client, db_session):
        """Test DELETE /api/exercises/<id> deletes exercise."""
        exercise = Exercise(
            name='Lunges',
            category='strength',
            muscle_group='legs'
        )
        db_session.add(exercise)
        db_session.commit()
        exercise_id = exercise.id
        
        response = client.delete(f'/api/exercises/{exercise_id}')
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f'/api/exercises/{exercise_id}')
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_filter_exercises_by_category(self, client, db_session):
        """Test filtering exercises by category."""
        exercise1 = Exercise(name='Bench Press', category='strength', muscle_group='chest')
        exercise2 = Exercise(name='Running', category='cardio', muscle_group='legs')
        db_session.add_all([exercise1, exercise2])
        db_session.commit()
        
        response = client.get('/api/exercises?category=strength')
        assert response.status_code == 200
        data = response.get_json()
        
        exercises = data['exercises']
        assert all(e['category'] == 'strength' for e in exercises)
    
    @pytest.mark.api
    def test_filter_exercises_by_muscle_group(self, client, db_session):
        """Test filtering exercises by muscle group."""
        exercise1 = Exercise(name='Squats', category='strength', muscle_group='legs')
        exercise2 = Exercise(name='Bench Press', category='strength', muscle_group='chest')
        db_session.add_all([exercise1, exercise2])
        db_session.commit()
        
        response = client.get('/api/exercises?muscle_group=legs')
        assert response.status_code == 200
        data = response.get_json()
        
        exercises = data['exercises']
        assert all(e['muscle_group'] == 'legs' for e in exercises)
    
    @pytest.mark.api
    def test_search_exercises(self, client, db_session):
        """Test searching exercises by name."""
        exercise1 = Exercise(name='Bench Press', category='strength', muscle_group='chest')
        exercise2 = Exercise(name='Incline Press', category='strength', muscle_group='chest')
        exercise3 = Exercise(name='Squats', category='strength', muscle_group='legs')
        db_session.add_all([exercise1, exercise2, exercise3])
        db_session.commit()
        
        response = client.get('/api/exercises?search=Press')
        assert response.status_code == 200
        data = response.get_json()
        
        exercises = data['exercises']
        assert len(exercises) >= 2
        assert all('Press' in e['name'] for e in exercises)
    
    @pytest.mark.api
    def test_exercise_pagination(self, client, db_session):
        """Test exercise pagination."""
        # Create multiple exercises
        for i in range(15):
            exercise = Exercise(
                name=f'Exercise {i}',
                category='strength',
                muscle_group='chest'
            )
            db_session.add(exercise)
        db_session.commit()
        
        # Get first page
        response = client.get('/api/exercises?page=1&per_page=10')
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data['exercises']) <= 10
        assert data['current_page'] == 1
        assert 'total' in data
        assert 'pages' in data
