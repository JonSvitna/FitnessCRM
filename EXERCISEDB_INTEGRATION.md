# ExerciseDB Integration Guide 🏋️

**API**: https://exercisedb.p.rapidapi.com/  
**Documentation**: https://rapidapi.com/justin-WFnsXH_t6/api/exercisedb  
**Strategy**: No caching - fetch from API on every request

---

## Overview

ExerciseDB provides access to 1,300+ exercises with detailed information including:
- Exercise names and descriptions
- Body parts and target muscles
- Equipment requirements
- GIF animations
- Instructions

**Why No Caching?**
- Prevents API ban from excessive caching
- Always fresh data
- Respects API terms of service
- Simple implementation

---

## Implementation Plan

### Step 1: Get API Credentials

1. Sign up at https://rapidapi.com
2. Subscribe to ExerciseDB API (Free tier: 100 requests/day)
3. Get your API key from RapidAPI dashboard

### Step 2: Configure Environment

Add to `backend/.env`:
```env
# ExerciseDB API Configuration
EXERCISEDB_API_KEY=your_rapidapi_key_here
EXERCISEDB_API_HOST=exercisedb.p.rapidapi.com
```

### Step 3: Create ExerciseDB Service

Create `backend/utils/exercisedb_service.py`:

```python
"""
ExerciseDB API Integration Service
Fetches exercise data from ExerciseDB API without caching
"""
import requests
import os
from utils.logger import logger

class ExerciseDBService:
    """Service for interacting with ExerciseDB API"""
    
    BASE_URL = "https://exercisedb.p.rapidapi.com"
    
    def __init__(self):
        self.api_key = os.getenv('EXERCISEDB_API_KEY')
        self.api_host = os.getenv('EXERCISEDB_API_HOST', 'exercisedb.p.rapidapi.com')
        
        if not self.api_key:
            logger.warning("ExerciseDB API key not configured. Exercise library will be limited.")
    
    def _make_request(self, endpoint, params=None):
        """Make request to ExerciseDB API"""
        if not self.api_key:
            return None
        
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"ExerciseDB API error: {str(e)}")
            return None
    
    def get_all_exercises(self, limit=None, offset=0):
        """
        Get all exercises (no caching)
        
        Args:
            limit: Number of exercises to return (default: all)
            offset: Number of exercises to skip
        
        Returns:
            List of exercise dictionaries
        """
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        return self._make_request('exercises', params)
    
    def get_exercise_by_id(self, exercise_id):
        """
        Get specific exercise by ID
        
        Args:
            exercise_id: ExerciseDB exercise ID
        
        Returns:
            Exercise dictionary
        """
        return self._make_request(f'exercises/exercise/{exercise_id}')
    
    def get_exercises_by_body_part(self, body_part):
        """
        Get exercises by body part
        
        Args:
            body_part: Body part (e.g., 'back', 'chest', 'legs')
        
        Returns:
            List of exercise dictionaries
        """
        return self._make_request(f'exercises/bodyPart/{body_part}')
    
    def get_exercises_by_equipment(self, equipment):
        """
        Get exercises by equipment
        
        Args:
            equipment: Equipment type (e.g., 'barbell', 'dumbbell', 'bodyweight')
        
        Returns:
            List of exercise dictionaries
        """
        return self._make_request(f'exercises/equipment/{equipment}')
    
    def get_exercises_by_target(self, target):
        """
        Get exercises by target muscle
        
        Args:
            target: Target muscle (e.g., 'biceps', 'quads', 'glutes')
        
        Returns:
            List of exercise dictionaries
        """
        return self._make_request(f'exercises/target/{target}')
    
    def get_body_part_list(self):
        """Get list of all body parts"""
        return self._make_request('exercises/bodyPartList')
    
    def get_target_list(self):
        """Get list of all target muscles"""
        return self._make_request('exercises/targetList')
    
    def get_equipment_list(self):
        """Get list of all equipment types"""
        return self._make_request('exercises/equipmentList')
    
    def search_exercises(self, name):
        """
        Search exercises by name
        
        Args:
            name: Exercise name to search
        
        Returns:
            List of exercise dictionaries
        """
        return self._make_request(f'exercises/name/{name}')
    
    def format_exercise(self, api_exercise):
        """
        Format ExerciseDB API response to match our Exercise model
        
        Args:
            api_exercise: Raw exercise data from API
        
        Returns:
            Formatted exercise dictionary
        """
        if not api_exercise:
            return None
        
        return {
            'external_id': api_exercise.get('id'),  # ExerciseDB ID
            'name': api_exercise.get('name', '').title(),
            'body_part': api_exercise.get('bodyPart'),
            'target': api_exercise.get('target'),
            'equipment': api_exercise.get('equipment'),
            'gif_url': api_exercise.get('gifUrl'),
            'secondary_muscles': api_exercise.get('secondaryMuscles', []),
            'instructions': api_exercise.get('instructions', [])
        }

# Singleton instance
exercisedb_service = ExerciseDBService()
```

### Step 4: Update Exercise Routes

Modify `backend/api/exercise_routes.py`:

```python
"""
Exercise library API routes with ExerciseDB integration
"""
from flask import Blueprint, request, jsonify
from models.database import db, Exercise
from utils.exercisedb_service import exercisedb_service
from utils.logger import logger

exercise_bp = Blueprint('exercises', __name__, url_prefix='/api/exercises')

@exercise_bp.route('/library', methods=['GET'])
def get_exercise_library():
    """
    Get exercises from ExerciseDB API (no caching)
    
    Query params:
        - body_part: Filter by body part
        - equipment: Filter by equipment
        - target: Filter by target muscle
        - search: Search by name
        - limit: Number of results (default: 20)
        - offset: Pagination offset (default: 0)
    """
    try:
        body_part = request.args.get('body_part')
        equipment = request.args.get('equipment')
        target = request.args.get('target')
        search = request.args.get('search')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        exercises = None
        
        # Filter by body part
        if body_part:
            exercises = exercisedb_service.get_exercises_by_body_part(body_part)
        
        # Filter by equipment
        elif equipment:
            exercises = exercisedb_service.get_exercises_by_equipment(equipment)
        
        # Filter by target muscle
        elif target:
            exercises = exercisedb_service.get_exercises_by_target(target)
        
        # Search by name
        elif search:
            exercises = exercisedb_service.search_exercises(search)
        
        # Get all exercises
        else:
            exercises = exercisedb_service.get_all_exercises(limit=limit, offset=offset)
        
        if exercises is None:
            return jsonify({
                'error': 'ExerciseDB API not configured or unavailable',
                'exercises': []
            }), 503
        
        # Format exercises
        formatted_exercises = [
            exercisedb_service.format_exercise(ex) for ex in exercises
        ]
        
        # Apply pagination if needed (when not already paginated by API)
        if limit and offset == 0:
            formatted_exercises = formatted_exercises[:limit]
        
        return jsonify({
            'exercises': formatted_exercises,
            'total': len(formatted_exercises),
            'source': 'exercisedb',
            'cached': False  # Always False - no caching
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching exercises: {str(e)}")
        return jsonify({'error': str(e)}), 500

@exercise_bp.route('/library/<exercise_id>', methods=['GET'])
def get_exercise_detail(exercise_id):
    """Get specific exercise from ExerciseDB by ID (no caching)"""
    try:
        exercise = exercisedb_service.get_exercise_by_id(exercise_id)
        
        if not exercise:
            return jsonify({'error': 'Exercise not found or API unavailable'}), 404
        
        formatted = exercisedb_service.format_exercise(exercise)
        
        return jsonify({
            'exercise': formatted,
            'source': 'exercisedb',
            'cached': False
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching exercise detail: {str(e)}")
        return jsonify({'error': str(e)}), 500

@exercise_bp.route('/library/body-parts', methods=['GET'])
def get_body_parts():
    """Get list of available body parts from ExerciseDB (no caching)"""
    try:
        body_parts = exercisedb_service.get_body_part_list()
        
        if not body_parts:
            return jsonify({'error': 'API unavailable'}), 503
        
        return jsonify({
            'body_parts': body_parts,
            'cached': False
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exercise_bp.route('/library/targets', methods=['GET'])
def get_targets():
    """Get list of available target muscles from ExerciseDB (no caching)"""
    try:
        targets = exercisedb_service.get_target_list()
        
        if not targets:
            return jsonify({'error': 'API unavailable'}), 503
        
        return jsonify({
            'targets': targets,
            'cached': False
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exercise_bp.route('/library/equipment', methods=['GET'])
def get_equipment():
    """Get list of available equipment types from ExerciseDB (no caching)"""
    try:
        equipment = exercisedb_service.get_equipment_list()
        
        if not equipment:
            return jsonify({'error': 'API unavailable'}), 503
        
        return jsonify({
            'equipment': equipment,
            'cached': False
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Keep existing routes for custom exercises
@exercise_bp.route('/custom', methods=['GET'])
def get_custom_exercises():
    """Get custom exercises created by trainers (from database)"""
    try:
        query = Exercise.query.filter_by(is_custom=True)
        
        # Search
        search = request.args.get('search')
        if search:
            query = query.filter(Exercise.name.ilike(f'%{search}%'))
        
        # Filter by category
        category = request.args.get('category')
        if category:
            query = query.filter_by(category=category)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        exercises_paginated = query.order_by(Exercise.name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'exercises': [e.to_dict() for e in exercises_paginated.items],
            'total': exercises_paginated.total,
            'pages': exercises_paginated.pages,
            'current_page': page,
            'source': 'database',
            'cached': True  # From database
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exercise_bp.route('/custom', methods=['POST'])
def create_custom_exercise():
    """Create a custom exercise (stored in database)"""
    try:
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({'error': 'name is required'}), 400
        
        exercise = Exercise(
            name=data['name'],
            category=data.get('category'),
            muscle_group=data.get('muscle_group'),
            equipment=data.get('equipment'),
            difficulty=data.get('difficulty'),
            description=data.get('description'),
            instructions=data.get('instructions'),
            tips=data.get('tips'),
            image_url=data.get('image_url'),
            video_url=data.get('video_url'),
            is_custom=True,
            created_by=data.get('created_by')
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        return jsonify({
            'message': 'Custom exercise created successfully',
            'exercise': exercise.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
```

### Step 5: Install Dependencies

Add to `backend/requirements.txt`:
```
requests>=2.31.0
```

Install:
```bash
cd backend
pip install requests
```

### Step 6: Frontend Integration

Update `frontend/src/main.js` or create `frontend/src/exerciseLibrary.js`:

```javascript
// Exercise Library with ExerciseDB Integration

class ExerciseLibrary {
    constructor() {
        this.api = axios.create({
            baseURL: import.meta.env.VITE_API_URL
        });
    }
    
    // Get exercises from ExerciseDB (no caching)
    async getExercises(filters = {}) {
        const params = new URLSearchParams();
        
        if (filters.bodyPart) params.append('body_part', filters.bodyPart);
        if (filters.equipment) params.append('equipment', filters.equipment);
        if (filters.target) params.append('target', filters.target);
        if (filters.search) params.append('search', filters.search);
        if (filters.limit) params.append('limit', filters.limit);
        if (filters.offset) params.append('offset', filters.offset);
        
        const response = await this.api.get(`/api/exercises/library?${params}`);
        return response.data;
    }
    
    // Get exercise detail
    async getExerciseDetail(exerciseId) {
        const response = await this.api.get(`/api/exercises/library/${exerciseId}`);
        return response.data;
    }
    
    // Get filter options
    async getBodyParts() {
        const response = await this.api.get('/api/exercises/library/body-parts');
        return response.data.body_parts;
    }
    
    async getTargets() {
        const response = await this.api.get('/api/exercises/library/targets');
        return response.data.targets;
    }
    
    async getEquipment() {
        const response = await this.api.get('/api/exercises/library/equipment');
        return response.data.equipment;
    }
    
    // Get custom exercises (from database)
    async getCustomExercises(page = 1) {
        const response = await this.api.get(`/api/exercises/custom?page=${page}`);
        return response.data;
    }
    
    // Create custom exercise
    async createCustomExercise(exerciseData) {
        const response = await this.api.post('/api/exercises/custom', exerciseData);
        return response.data;
    }
    
    // Render exercise card
    renderExerciseCard(exercise) {
        return `
            <div class="exercise-card bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div class="aspect-video bg-gray-900 rounded mb-3">
                    ${exercise.gif_url ? 
                        `<img src="${exercise.gif_url}" alt="${exercise.name}" class="w-full h-full object-cover rounded">` :
                        `<div class="w-full h-full flex items-center justify-center text-gray-500">No preview</div>`
                    }
                </div>
                <h3 class="text-lg font-semibold text-white mb-2">${exercise.name}</h3>
                <div class="flex flex-wrap gap-2 mb-2">
                    ${exercise.body_part ? `<span class="px-2 py-1 bg-orange-600 text-white text-xs rounded">${exercise.body_part}</span>` : ''}
                    ${exercise.equipment ? `<span class="px-2 py-1 bg-gray-700 text-white text-xs rounded">${exercise.equipment}</span>` : ''}
                    ${exercise.target ? `<span class="px-2 py-1 bg-blue-600 text-white text-xs rounded">${exercise.target}</span>` : ''}
                </div>
                <button onclick="exerciseLibrary.viewDetails('${exercise.external_id}')" 
                        class="w-full bg-orange-600 hover:bg-orange-700 text-white py-2 rounded">
                    View Details
                </button>
            </div>
        `;
    }
    
    // View exercise details modal
    async viewDetails(exerciseId) {
        const { exercise } = await this.getExerciseDetail(exerciseId);
        
        const modal = `
            <div id="exercise-modal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
                <div class="bg-gray-800 rounded-lg p-6 max-w-2xl max-h-screen overflow-y-auto">
                    <div class="flex justify-between items-start mb-4">
                        <h2 class="text-2xl font-bold text-white">${exercise.name}</h2>
                        <button onclick="document.getElementById('exercise-modal').remove()" 
                                class="text-gray-400 hover:text-white">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    ${exercise.gif_url ? `
                        <div class="aspect-video bg-gray-900 rounded mb-4">
                            <img src="${exercise.gif_url}" alt="${exercise.name}" class="w-full h-full object-contain rounded">
                        </div>
                    ` : ''}
                    
                    <div class="space-y-4">
                        <div>
                            <h3 class="font-semibold text-white mb-2">Target Muscle</h3>
                            <p class="text-gray-300">${exercise.target}</p>
                        </div>
                        
                        ${exercise.secondary_muscles?.length ? `
                            <div>
                                <h3 class="font-semibold text-white mb-2">Secondary Muscles</h3>
                                <p class="text-gray-300">${exercise.secondary_muscles.join(', ')}</p>
                            </div>
                        ` : ''}
                        
                        <div>
                            <h3 class="font-semibold text-white mb-2">Equipment</h3>
                            <p class="text-gray-300">${exercise.equipment}</p>
                        </div>
                        
                        ${exercise.instructions?.length ? `
                            <div>
                                <h3 class="font-semibold text-white mb-2">Instructions</h3>
                                <ol class="list-decimal list-inside text-gray-300 space-y-2">
                                    ${exercise.instructions.map(inst => `<li>${inst}</li>`).join('')}
                                </ol>
                            </div>
                        ` : ''}
                        
                        <button onclick="exerciseLibrary.addToWorkout('${exercise.external_id}')" 
                                class="w-full bg-orange-600 hover:bg-orange-700 text-white py-3 rounded">
                            Add to Workout
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modal);
    }
}

// Initialize
const exerciseLibrary = new ExerciseLibrary();
```

---

## API Rate Limiting Strategy

Since we're not caching, we need to be mindful of rate limits:

### Free Tier Limits
- 100 requests per day
- ~4 requests per hour sustained

### Best Practices

1. **Pagination**: Request only needed data
   ```javascript
   // Load 20 exercises at a time
   const exercises = await exerciseLibrary.getExercises({ limit: 20 });
   ```

2. **Lazy Loading**: Load more as user scrolls
   ```javascript
   let offset = 0;
   async function loadMore() {
       const data = await exerciseLibrary.getExercises({ 
           limit: 20, 
           offset: offset 
       });
       offset += 20;
       renderExercises(data.exercises);
   }
   ```

3. **Smart Filtering**: Filter on backend before fetching
   ```javascript
   // Instead of fetching all and filtering client-side:
   const exercises = await exerciseLibrary.getExercises({ 
       bodyPart: 'chest',
       equipment: 'barbell'
   });
   ```

4. **User-triggered Requests**: Don't auto-load
   - Require user to click "Search" or "Load More"
   - Don't refresh automatically
   - Debounce search inputs (500ms delay)

5. **Fallback to Custom Exercises**: If quota exceeded
   ```javascript
   try {
       const exercises = await exerciseLibrary.getExercises(filters);
   } catch (error) {
       if (error.response?.status === 429) {
           // Rate limit exceeded, show custom exercises
           const customExercises = await exerciseLibrary.getCustomExercises();
           showNotification('Using custom exercises (API limit reached)');
       }
   }
   ```

---

## Testing

### Test API Connection

Create `backend/test_exercisedb.py`:

```python
"""Test ExerciseDB integration"""
import os
from dotenv import load_dotenv
from utils.exercisedb_service import exercisedb_service

load_dotenv()

def test_connection():
    """Test basic API connection"""
    print("Testing ExerciseDB API connection...")
    
    # Test get all exercises
    exercises = exercisedb_service.get_all_exercises(limit=5)
    if exercises:
        print(f"✓ Successfully fetched {len(exercises)} exercises")
        print(f"  First exercise: {exercises[0].get('name')}")
    else:
        print("✗ Failed to fetch exercises")
    
    # Test body parts
    body_parts = exercisedb_service.get_body_part_list()
    if body_parts:
        print(f"✓ Found {len(body_parts)} body parts")
    
    # Test equipment
    equipment = exercisedb_service.get_equipment_list()
    if equipment:
        print(f"✓ Found {len(equipment)} equipment types")

if __name__ == '__main__':
    test_connection()
```

Run:
```bash
cd backend
python test_exercisedb.py
```

---

## Deployment Checklist

- [ ] Sign up for RapidAPI account
- [ ] Subscribe to ExerciseDB API
- [ ] Add API key to environment variables
- [ ] Install requests library
- [ ] Create exercisedb_service.py
- [ ] Update exercise_routes.py with new endpoints
- [ ] Test API connection
- [ ] Update frontend to use new endpoints
- [ ] Test rate limiting behavior
- [ ] Document for users

---

## Monitoring API Usage

Add to `backend/utils/exercisedb_service.py`:

```python
from datetime import datetime, timedelta

class ExerciseDBService:
    def __init__(self):
        # ... existing code ...
        self.request_count = 0
        self.request_reset = datetime.utcnow() + timedelta(days=1)
    
    def _make_request(self, endpoint, params=None):
        # Check if daily limit approaching
        if self.request_count >= 95:  # 95 out of 100
            logger.warning(f"ExerciseDB API: {self.request_count}/100 requests used today")
        
        # ... existing request code ...
        
        self.request_count += 1
        
        # Reset counter daily
        if datetime.utcnow() > self.request_reset:
            self.request_count = 0
            self.request_reset = datetime.utcnow() + timedelta(days=1)
        
        return response.json()
```

---

## Alternative: Upgrade Plans

If 100 requests/day is not enough:

| Plan | Requests | Cost |
|------|----------|------|
| Basic | 500/day | $10/month |
| Pro | 2,500/day | $25/month |
| Ultra | 10,000/day | $50/month |

---

## Summary

✅ **No Caching Strategy**
- Fetch from API on every request
- Respects API terms of service
- Avoids ban risk
- Always fresh data

⚠️ **Rate Limiting**
- Monitor usage (100/day free tier)
- Implement smart pagination
- User-triggered requests only
- Fallback to custom exercises

🎯 **Implementation**
- Simple service layer
- New API routes
- Frontend integration
- Monitoring included

**Estimated Time**: 4-6 hours
**Complexity**: Low-Medium
**Risk**: Low (no caching = simple + compliant)
