"""
ExerciseDB API Integration Service
Fetches exercise data from ExerciseDB API without caching to prevent API ban
API Documentation: https://rapidapi.com/justin-WFnsXH_t6/api/exercisedb
"""
import requests
import os
from datetime import datetime, timedelta
from utils.logger import logger

class ExerciseDBService:
    """Service for interacting with ExerciseDB API - NO CACHING to prevent API ban"""
    
    BASE_URL = "https://exercisedb.p.rapidapi.com"
    
    def __init__(self):
        self.api_key = os.getenv('EXERCISEDB_API_KEY')
        self.api_host = os.getenv('EXERCISEDB_API_HOST', 'exercisedb.p.rapidapi.com')
        
        # Simple request counter for monitoring (resets daily)
        self.request_count = 0
        self.request_reset = datetime.utcnow() + timedelta(days=1)
        
        if not self.api_key:
            logger.warning("ExerciseDB API key not configured. Exercise library will be limited to custom exercises only.")
    
    def _make_request(self, endpoint, params=None):
        """
        Make request to ExerciseDB API
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
        
        Returns:
            JSON response or None if error
        """
        if not self.api_key:
            logger.error("ExerciseDB API key not configured")
            return None
        
        # Reset counter if day has passed
        if datetime.utcnow() > self.request_reset:
            self.request_count = 0
            self.request_reset = datetime.utcnow() + timedelta(days=1)
        
        # Warn if approaching free tier limit (100/day)
        if self.request_count >= 95:
            logger.warning(f"ExerciseDB API: {self.request_count}/100 requests used today. Consider upgrading plan.")
        
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            self.request_count += 1
            logger.info(f"ExerciseDB API request to {endpoint} - Count: {self.request_count}/100")
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error("ExerciseDB API rate limit exceeded (429)")
            else:
                logger.error(f"ExerciseDB API HTTP error: {e.response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            logger.error("ExerciseDB API request timeout")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ExerciseDB API error: {str(e)}")
            return None
    
    def get_all_exercises(self, limit=None, offset=0):
        """
        Get all exercises from ExerciseDB (NO CACHING)
        
        Args:
            limit: Number of exercises to return (default: 10, max recommended: 50)
            offset: Number of exercises to skip for pagination
        
        Returns:
            List of exercise dictionaries or None if error
        """
        # Use reasonable defaults to avoid excessive API calls
        if limit is None:
            limit = 10
        
        params = {'limit': limit, 'offset': offset}
        
        return self._make_request('exercises', params)
    
    def get_exercise_by_id(self, exercise_id):
        """
        Get specific exercise by ID from ExerciseDB (NO CACHING)
        
        Args:
            exercise_id: ExerciseDB exercise ID
        
        Returns:
            Exercise dictionary or None if error
        """
        return self._make_request(f'exercises/exercise/{exercise_id}')
    
    def get_exercises_by_body_part(self, body_part):
        """
        Get exercises by body part from ExerciseDB (NO CACHING)
        
        Args:
            body_part: Body part (e.g., 'back', 'chest', 'legs', 'shoulders')
        
        Returns:
            List of exercise dictionaries or None if error
        """
        return self._make_request(f'exercises/bodyPart/{body_part}')
    
    def get_exercises_by_equipment(self, equipment):
        """
        Get exercises by equipment from ExerciseDB (NO CACHING)
        
        Args:
            equipment: Equipment type (e.g., 'barbell', 'dumbbell', 'bodyweight')
        
        Returns:
            List of exercise dictionaries or None if error
        """
        return self._make_request(f'exercises/equipment/{equipment}')
    
    def get_exercises_by_target(self, target):
        """
        Get exercises by target muscle from ExerciseDB (NO CACHING)
        
        Args:
            target: Target muscle (e.g., 'biceps', 'quads', 'glutes', 'abs')
        
        Returns:
            List of exercise dictionaries or None if error
        """
        return self._make_request(f'exercises/target/{target}')
    
    def get_body_part_list(self):
        """
        Get list of all available body parts from ExerciseDB (NO CACHING)
        
        Returns:
            List of body part strings or None if error
        """
        return self._make_request('exercises/bodyPartList')
    
    def get_target_list(self):
        """
        Get list of all available target muscles from ExerciseDB (NO CACHING)
        
        Returns:
            List of target muscle strings or None if error
        """
        return self._make_request('exercises/targetList')
    
    def get_equipment_list(self):
        """
        Get list of all available equipment types from ExerciseDB (NO CACHING)
        
        Returns:
            List of equipment type strings or None if error
        """
        return self._make_request('exercises/equipmentList')
    
    def search_exercises(self, name):
        """
        Search exercises by name from ExerciseDB (NO CACHING)
        
        Args:
            name: Exercise name to search (e.g., 'push up', 'squat')
        
        Returns:
            List of exercise dictionaries or None if error
        """
        return self._make_request(f'exercises/name/{name}')
    
    def format_exercise(self, api_exercise):
        """
        Format ExerciseDB API response to standardized format
        
        Args:
            api_exercise: Raw exercise data from ExerciseDB API
        
        Returns:
            Formatted exercise dictionary or None if invalid input
        """
        if not api_exercise:
            return None
        
        return {
            'external_id': api_exercise.get('id'),  # ExerciseDB ID for reference
            'name': api_exercise.get('name', '').replace('_', ' ').title(),
            'body_part': api_exercise.get('bodyPart', '').title(),
            'target': api_exercise.get('target', '').title(),
            'equipment': api_exercise.get('equipment', '').title(),
            'gif_url': api_exercise.get('gifUrl'),
            'secondary_muscles': [m.title() for m in api_exercise.get('secondaryMuscles', [])],
            'instructions': api_exercise.get('instructions', []),
            'source': 'exercisedb',
            'cached': False  # Always False - no caching to prevent API ban
        }
    
    def get_request_usage(self):
        """
        Get current API request usage statistics
        
        Returns:
            Dictionary with usage stats
        """
        return {
            'requests_used': self.request_count,
            'requests_limit': 100,  # Free tier limit
            'reset_time': self.request_reset.isoformat(),
            'percentage_used': (self.request_count / 100) * 100
        }

# Singleton instance
exercisedb_service = ExerciseDBService()
