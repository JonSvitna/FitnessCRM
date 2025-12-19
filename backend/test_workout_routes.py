"""
Unit tests for workout template API routes.
"""

import pytest
from models.database import WorkoutTemplate, Exercise, WorkoutExercise, Trainer


class TestWorkoutTemplateRoutes:
    """Test workout template API endpoints."""
    
    @pytest.mark.api
    def test_get_templates(self, client):
        """Test GET /api/workouts/templates returns template list."""
        response = client.get('/api/workouts/templates')
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'templates' in data
        assert 'total' in data
        assert isinstance(data['templates'], list)
    
    @pytest.mark.api
    def test_create_template(self, client, db_session, sample_trainer):
        """Test POST /api/workouts/templates creates a template."""
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        template_data = {
            'name': 'Full Body Workout',
            'description': 'Complete full body strength training',
            'category': 'strength',
            'difficulty': 'intermediate',
            'duration_minutes': 60,
            'created_by': trainer.id,
            'is_public': True
        }
        response = client.post('/api/workouts/templates', json=template_data)
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data
        assert data['name'] == 'Full Body Workout'
        assert data['created_by'] == trainer.id
    
    @pytest.mark.api
    def test_create_template_missing_fields(self, client):
        """Test POST /api/workouts/templates without required fields."""
        template_data = {
            'description': 'Missing name and created_by'
        }
        response = client.post('/api/workouts/templates', json=template_data)
        assert response.status_code == 400
    
    @pytest.mark.api
    def test_get_template_by_id(self, client, db_session, sample_trainer):
        """Test GET /api/workouts/templates/<id> returns specific template."""
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        template = WorkoutTemplate(
            name='Upper Body',
            category='strength',
            created_by=trainer.id
        )
        db_session.add(template)
        db_session.commit()
        
        response = client.get(f'/api/workouts/templates/{template.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['id'] == template.id
        assert data['name'] == 'Upper Body'
    
    @pytest.mark.api
    def test_update_template(self, client, db_session, sample_trainer):
        """Test PUT /api/workouts/templates/<id> updates template."""
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        template = WorkoutTemplate(
            name='Lower Body',
            category='strength',
            created_by=trainer.id
        )
        db_session.add(template)
        db_session.commit()
        
        update_data = {
            'description': 'Updated description',
            'difficulty': 'advanced'
        }
        response = client.put(f'/api/workouts/templates/{template.id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['description'] == 'Updated description'
        assert data['difficulty'] == 'advanced'
    
    @pytest.mark.api
    def test_delete_template(self, client, db_session, sample_trainer):
        """Test DELETE /api/workouts/templates/<id> deletes template."""
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        template = WorkoutTemplate(
            name='Core Workout',
            category='strength',
            created_by=trainer.id
        )
        db_session.add(template)
        db_session.commit()
        template_id = template.id
        
        response = client.delete(f'/api/workouts/templates/{template_id}')
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f'/api/workouts/templates/{template_id}')
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_filter_templates_by_creator(self, client, db_session, sample_trainer):
        """Test filtering templates by creator."""
        trainer1 = Trainer(**sample_trainer)
        trainer2_data = sample_trainer.copy()
        trainer2_data['email'] = 'trainer2@example.com'
        trainer2 = Trainer(**trainer2_data)
        db_session.add_all([trainer1, trainer2])
        db_session.commit()
        
        template1 = WorkoutTemplate(name='Workout 1', category='strength', created_by=trainer1.id)
        template2 = WorkoutTemplate(name='Workout 2', category='cardio', created_by=trainer2.id)
        db_session.add_all([template1, template2])
        db_session.commit()
        
        response = client.get(f'/api/workouts/templates?created_by={trainer1.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        templates = data['templates']
        assert all(t['created_by'] == trainer1.id for t in templates)
    
    @pytest.mark.api
    def test_filter_templates_by_category(self, client, db_session, sample_trainer):
        """Test filtering templates by category."""
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        template1 = WorkoutTemplate(name='Strength', category='strength', created_by=trainer.id)
        template2 = WorkoutTemplate(name='Cardio', category='cardio', created_by=trainer.id)
        db_session.add_all([template1, template2])
        db_session.commit()
        
        response = client.get('/api/workouts/templates?category=strength')
        assert response.status_code == 200
        data = response.get_json()
        
        templates = data['templates']
        assert all(t['category'] == 'strength' for t in templates)
    
    @pytest.mark.api
    def test_search_templates(self, client, db_session, sample_trainer):
        """Test searching templates by name."""
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        template1 = WorkoutTemplate(name='Full Body Strength', category='strength', created_by=trainer.id)
        template2 = WorkoutTemplate(name='Upper Body Strength', category='strength', created_by=trainer.id)
        template3 = WorkoutTemplate(name='Cardio Blast', category='cardio', created_by=trainer.id)
        db_session.add_all([template1, template2, template3])
        db_session.commit()
        
        response = client.get('/api/workouts/templates?search=Strength')
        assert response.status_code == 200
        data = response.get_json()
        
        templates = data['templates']
        assert len(templates) >= 2
        assert all('Strength' in t['name'] for t in templates)
    
    @pytest.mark.integration
    def test_template_with_exercises(self, client, db_session, sample_trainer):
        """Test creating template with exercises."""
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        # Create exercises
        exercise1 = Exercise(name='Squats', category='strength', muscle_group='legs')
        exercise2 = Exercise(name='Bench Press', category='strength', muscle_group='chest')
        db_session.add_all([exercise1, exercise2])
        db_session.commit()
        
        # Create template
        template = WorkoutTemplate(
            name='Full Body',
            category='strength',
            created_by=trainer.id
        )
        db_session.add(template)
        db_session.flush()
        
        # Add exercises to template
        workout_ex1 = WorkoutExercise(
            template_id=template.id,
            exercise_id=exercise1.id,
            sets=3,
            reps=10,
            order_index=1
        )
        workout_ex2 = WorkoutExercise(
            template_id=template.id,
            exercise_id=exercise2.id,
            sets=3,
            reps=12,
            order_index=2
        )
        db_session.add_all([workout_ex1, workout_ex2])
        db_session.commit()
        
        # Get template and verify exercises
        response = client.get(f'/api/workouts/templates/{template.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        # Template should exist
        assert data['id'] == template.id
