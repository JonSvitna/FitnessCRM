import './styles/main.css';
import { trainerAPI, clientAPI, crmAPI, settingsAPI, sessionAPI, workoutAPI, exerciseAPI } from './api.js';
import { requireRole, auth } from './auth.js';

// Helper function to extract data from API responses
function extractData(response) {
  // Handle paginated responses {items: [...], total: N} or direct arrays
  return response.data?.items || response.data || [];
}

// State management
let state = {
  trainer: null, // Will be loaded from authenticated user
  trainerId: null, // Trainer ID from user profile
  clients: [],
  assignments: [],
  workouts: [],
  sessions: [],
  messages: [],
  challenges: [],
  sidebarExpanded: true,
};

// Helper function to get trainer's clients
function getMyClients() {
  const myAssignments = state.assignments.filter(a => a.trainer_id === state.trainer.id);
  const myClientIds = myAssignments.map(a => a.client_id);
  return state.clients.filter(c => myClientIds.includes(c.id));
}

// Sidebar functionality
function initSidebar() {
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('main-content');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
  const mobileOverlay = document.getElementById('mobile-overlay');
  const collapseIcon = document.getElementById('collapse-icon');
  const sidebarLogoText = document.getElementById('sidebar-logo-text');

  if (!sidebar || !mainContent) return;

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      state.sidebarExpanded = !state.sidebarExpanded;
      
      if (state.sidebarExpanded) {
        sidebar.classList.remove('sidebar-collapsed');
        sidebar.classList.add('sidebar-expanded');
        mainContent.classList.remove('main-content-collapsed');
        mainContent.classList.add('main-content-expanded');
        if (sidebarLogoText) sidebarLogoText.classList.remove('hidden');
        document.querySelectorAll('.sidebar-label').forEach(label => label.classList.remove('hidden'));
      } else {
        sidebar.classList.remove('sidebar-expanded');
        sidebar.classList.add('sidebar-collapsed');
        mainContent.classList.remove('main-content-expanded');
        mainContent.classList.add('main-content-collapsed');
        if (sidebarLogoText) sidebarLogoText.classList.add('hidden');
        document.querySelectorAll('.sidebar-label').forEach(label => label.classList.add('hidden'));
      }

      if (collapseIcon) {
        if (state.sidebarExpanded) {
          collapseIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"></path>';
        } else {
          collapseIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path>';
        }
      }
    });
  }

  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('sidebar-mobile-open');
      if (mobileOverlay) mobileOverlay.classList.toggle('hidden');
    });
  }

  if (mobileOverlay) {
    mobileOverlay.addEventListener('click', () => {
      sidebar.classList.remove('sidebar-mobile-open');
      mobileOverlay.classList.add('hidden');
    });
  }
}

function updatePageTitle(title) {
  const pageTitle = document.getElementById('page-title');
  if (pageTitle) pageTitle.textContent = title;
}

function closeMobileMenu() {
  const sidebar = document.getElementById('sidebar');
  const mobileOverlay = document.getElementById('mobile-overlay');
  if (sidebar) sidebar.classList.remove('sidebar-mobile-open');
  if (mobileOverlay) mobileOverlay.classList.add('hidden');
}

// Utility functions
function showToast(message, duration = 3000) {
  const toast = document.getElementById('toast');
  const toastMessage = document.getElementById('toast-message');
  toastMessage.textContent = message;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, duration);
}

function showSection(sectionId, title) {
  const sections = document.querySelectorAll('.section');
  sections.forEach(section => {
    section.classList.add('hidden');
    section.classList.remove('active');
  });
  const targetSection = document.getElementById(sectionId);
  if (targetSection) {
    targetSection.classList.remove('hidden');
    targetSection.classList.add('active');
  }

  const sidebarItems = document.querySelectorAll('.sidebar-item');
  sidebarItems.forEach(item => item.classList.remove('sidebar-item-active'));
  const activeNav = document.getElementById(`nav-${sectionId.replace('-section', '')}`);
  if (activeNav) activeNav.classList.add('sidebar-item-active');
  
  if (title) updatePageTitle(title);
  closeMobileMenu();

  // Save current section to localStorage for reload persistence
  localStorage.setItem('currentSection', sectionId);
  if (title) {
    localStorage.setItem('currentSectionTitle', title);
  }
}

// Navigation handlers - will be initialized in DOMContentLoaded
function initNavigation() {
  document.getElementById('nav-dashboard').addEventListener('click', () => {
    showSection('dashboard-section', 'Dashboard');
    loadDashboard();
  });

  document.getElementById('nav-clients').addEventListener('click', () => {
    showSection('clients-section', 'My Clients');
    loadClients();
  });

  document.getElementById('nav-workouts').addEventListener('click', () => {
    showSection('workouts-section', 'Workouts');
    loadWorkouts();
  });

  document.getElementById('nav-calendar').addEventListener('click', () => {
    showSection('calendar-section', 'Calendar');
    loadCalendar();
  });

  document.getElementById('nav-messages').addEventListener('click', () => {
    showSection('messages-section', 'Messages');
    loadMessages();
  });

  document.getElementById('nav-challenges').addEventListener('click', () => {
    showSection('challenges-section', 'Challenges');
    loadChallenges();
  });

  document.getElementById('nav-settings').addEventListener('click', () => {
    showSection('settings-section', 'Settings');
    loadSettings();
  });

  // Logout handler
  document.getElementById('logout-btn').addEventListener('click', () => {
    if (confirm('Are you sure you want to logout?')) {
      auth.removeToken();
      auth.removeUser();
      window.location.href = '/login.html';
    }
  });
}

// Dashboard functions
async function loadDashboard() {
  try {
    if (!state.trainer || !state.trainer.id) {
      console.error('Trainer not loaded');
      return;
    }

    const [clientsResponse, assignmentsResponse, sessionsResponse] = await Promise.all([
      clientAPI.getAll(),
      crmAPI.getAssignments(),
      sessionAPI.getAll({ trainer_id: state.trainer.id }).catch(() => ({ data: [] }))
    ]);

    state.clients = extractData(clientsResponse);
    state.assignments = assignmentsResponse.data;
    state.sessions = sessionsResponse.data || [];

    // Filter my clients (assignments for this trainer)
    const myAssignments = state.assignments.filter(a => a.trainer_id === state.trainer.id);
    const myClientIds = myAssignments.map(a => a.client_id);
    const myClients = state.clients.filter(c => myClientIds.includes(c.id));
    const activeClients = myClients.filter(c => c.status === 'active');

    document.getElementById('total-clients').textContent = myClients.length;
    document.getElementById('active-clients').textContent = activeClients.length;
    
    // Calculate this week's sessions
    const now = new Date();
    const weekStart = new Date(now);
    weekStart.setDate(now.getDate() - now.getDay()); // Start of week
    weekStart.setHours(0, 0, 0, 0);
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 7);
    
    const thisWeekSessions = state.sessions.filter(s => {
      const sessionDate = new Date(s.session_date);
      return sessionDate >= weekStart && sessionDate < weekEnd;
    });
    
    document.getElementById('sessions-this-week').textContent = thisWeekSessions.length;
    document.getElementById('new-messages').textContent = '0'; // TODO: Implement messages

    // Today's schedule
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    
    const todaySessions = state.sessions
      .filter(s => {
        const sessionDate = new Date(s.session_date);
        return sessionDate >= today && sessionDate < tomorrow;
      })
      .sort((a, b) => new Date(a.session_date) - new Date(b.session_date));
    
    const scheduleContainer = document.getElementById('today-schedule');
    if (todaySessions.length > 0) {
      scheduleContainer.innerHTML = todaySessions.map(session => {
        const client = state.clients.find(c => c.id === session.client_id);
        const sessionDate = new Date(session.session_date);
        return `
          <div class="p-3 bg-neutral-50 rounded-lg">
            <p class="text-neutral-900 font-medium">${client?.name || 'Unknown Client'}</p>
            <p class="text-sm text-neutral-600">${sessionDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${session.session_type || 'Session'} (${session.duration || 60} min)</p>
          </div>
        `;
      }).join('');
    } else {
      scheduleContainer.innerHTML = '<p class="text-neutral-600">No sessions scheduled for today</p>';
    }

    // Recent activity
    const activityContainer = document.getElementById('recent-activity');
    if (myAssignments.length > 0) {
      activityContainer.innerHTML = myAssignments.slice(0, 5).map(assignment => {
        const client = state.clients.find(c => c.id === assignment.client_id);
        return `
          <div class="flex items-center justify-between p-3 bg-neutral-50 rounded-lg">
            <div>
              <p class="text-neutral-900 font-medium">${client?.name || 'Unknown'}</p>
              <p class="text-sm text-neutral-600">Assigned ${new Date(assignment.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        `;
      }).join('');
    } else {
      activityContainer.innerHTML = '<p class="text-neutral-600">No recent activity</p>';
    }
  } catch (error) {
    console.error('Error loading dashboard:', error);
  }
}

// Clients functions
async function loadClients() {
  try {
    const [clientsResponse, assignmentsResponse] = await Promise.all([
      clientAPI.getAll(),
      crmAPI.getAssignments(),
    ]);

    state.clients = clientsResponse.data;
    state.assignments = assignmentsResponse.data;

    // Update client select for assignment form
    const clientSelect = document.querySelector('#assign-client-form select[name="client_id"]');
    const myAssignments = state.assignments.filter(a => a.trainer_id === state.trainer.id);
    const assignedClientIds = myAssignments.map(a => a.client_id);
    const unassignedClients = state.clients.filter(c => !assignedClientIds.includes(c.id));

    clientSelect.innerHTML = '<option value="">Choose a client...</option>' +
      unassignedClients.map(c => `<option value="${c.id}">${c.name} (${c.email})</option>`).join('');

    // Render my clients
    renderMyClients();
  } catch (error) {
    console.error('Error loading clients:', error);
  }
}

function renderMyClients() {
  const container = document.getElementById('clients-list');
  const myAssignments = state.assignments.filter(a => a.trainer_id === state.trainer.id);
  const myClientIds = myAssignments.map(a => a.client_id);
  const myClients = state.clients.filter(c => myClientIds.includes(c.id));

  if (myClients.length === 0) {
    container.innerHTML = '<p class="text-neutral-600">No clients assigned yet</p>';
    return;
  }

  container.innerHTML = myClients.map(client => {
    const assignment = myAssignments.find(a => a.client_id === client.id);
    return `
      <div class="p-4 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h4 class="text-lg font-semibold text-neutral-900">${client.name}</h4>
            <p class="text-sm text-neutral-600">${client.email}</p>
            ${client.phone ? `<p class="text-sm text-neutral-600">${client.phone}</p>` : ''}
            ${client.age ? `<p class="text-sm text-neutral-600 mt-2">Age: ${client.age}</p>` : ''}
            ${client.goals ? `<p class="text-sm text-orange-600 mt-2"><strong>Goals:</strong> ${client.goals}</p>` : ''}
            ${client.medical_conditions ? `<p class="text-sm text-red-600"><strong>Medical:</strong> ${client.medical_conditions}</p>` : ''}
            ${assignment?.notes ? `<p class="text-sm text-neutral-500 mt-2"><strong>Notes:</strong> ${assignment.notes}</p>` : ''}
            <span class="inline-block mt-2 px-3 py-1 text-xs rounded-full ${
              client.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
            }">${client.status || 'active'}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// State for workout creation
let workoutCreationState = {
  exercises: [],
  availableExercises: [],
  searchResults: []
};

// Workouts functions
async function loadWorkouts() {
  try {
    // Load available exercises for workout creation (only if not already loaded)
    if (workoutCreationState.availableExercises.length === 0) {
      const exercisesResponse = await exerciseAPI.getAll();
      workoutCreationState.availableExercises = exercisesResponse.data || [];
    }

    // Load workout templates
    const response = await workoutAPI.getAllTemplates({ created_by: state.trainer.id });
    state.workouts = response.data?.templates || response.data || [];

    const workoutsContainer = document.getElementById('workouts-list');
    
    if (state.workouts.length === 0) {
      workoutsContainer.innerHTML = '<p class="text-neutral-600">No workout plans created yet. Use the form to create your first plan!</p>';
      return;
    }

    // Display workout plans with view/edit capability
    workoutsContainer.innerHTML = state.workouts.map(workout => `
      <div class="p-4 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h4 class="text-lg font-semibold text-neutral-900">${workout.name}</h4>
            ${workout.description ? `<p class="text-sm text-neutral-600 mt-1">${workout.description}</p>` : ''}
            <div class="flex gap-4 mt-2">
              <span class="text-sm text-neutral-600">Difficulty: <span class="capitalize">${workout.difficulty || workout.difficulty_level || 'N/A'}</span></span>
              ${workout.duration_weeks ? `<span class="text-sm text-neutral-600">Duration: ${workout.duration_weeks} weeks</span>` : ''}
              ${workout.exercises && workout.exercises.length > 0 ? `<span class="text-sm text-orange-600">${workout.exercises.length} exercises</span>` : ''}
            </div>
          </div>
          <div class="flex gap-2">
            <button onclick="viewWorkout(${workout.id})" class="px-3 py-1 text-sm bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors">
              View/Edit
            </button>
            <button onclick="assignWorkoutToClient(${workout.id})" class="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
              Assign
            </button>
          </div>
        </div>
      </div>
    `).join('');
  } catch (error) {
    console.error('Error loading workouts:', error);
    const workoutsContainer = document.getElementById('workouts-list');
    workoutsContainer.innerHTML = '<p class="text-red-600">Error loading workout plans. Please try again.</p>';
  }
}

// Show enhanced workout creation modal
function showEnhancedWorkoutModal(existingWorkout = null) {
  const isEdit = !!existingWorkout;
  workoutCreationState.exercises = existingWorkout?.exercises || [];
  
  const modalHtml = `
    <div id="enhanced-workout-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-2xl font-bold text-neutral-900">${isEdit ? 'Edit' : 'Create'} Workout Plan</h2>
            <button onclick="closeEnhancedWorkoutModal()" class="text-neutral-600 hover:text-neutral-900">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <form id="enhanced-workout-form" class="space-y-6">
            <!-- Basic Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="form-label">Plan Name *</label>
                <input type="text" name="name" required class="input-field" placeholder="e.g., Beginner Strength" value="${existingWorkout?.name || ''}">
              </div>
              <div>
                <label class="form-label">Difficulty Level</label>
                <select name="difficulty" class="input-field">
                  <option value="beginner" ${existingWorkout?.difficulty === 'beginner' ? 'selected' : ''}>Beginner</option>
                  <option value="intermediate" ${existingWorkout?.difficulty === 'intermediate' ? 'selected' : ''}>Intermediate</option>
                  <option value="advanced" ${existingWorkout?.difficulty === 'advanced' ? 'selected' : ''}>Advanced</option>
                </select>
              </div>
            </div>
            
            <div>
              <label class="form-label">Description</label>
              <textarea name="description" class="input-field" rows="2" placeholder="Plan overview...">${existingWorkout?.description || ''}</textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="form-label">Duration (weeks)</label>
                <input type="number" name="duration_weeks" class="input-field" placeholder="8" value="${existingWorkout?.duration_weeks || ''}">
              </div>
              <div>
                <label class="form-label">Category</label>
                <select name="category" class="input-field">
                  <option value="">Select category...</option>
                  <option value="strength" ${existingWorkout?.category === 'strength' ? 'selected' : ''}>Strength Training</option>
                  <option value="cardio" ${existingWorkout?.category === 'cardio' ? 'selected' : ''}>Cardio</option>
                  <option value="flexibility" ${existingWorkout?.category === 'flexibility' ? 'selected' : ''}>Flexibility</option>
                  <option value="hiit" ${existingWorkout?.category === 'hiit' ? 'selected' : ''}>HIIT</option>
                  <option value="mixed" ${existingWorkout?.category === 'mixed' ? 'selected' : ''}>Mixed</option>
                </select>
              </div>
            </div>

            <!-- Exercises Section -->
            <div class="border-t pt-4">
              <h3 class="text-lg font-semibold text-neutral-900 mb-3">Exercises</h3>
              
              <!-- Exercise Search -->
              <div class="mb-4">
                <label class="form-label">Search Exercises</label>
                <div class="flex gap-2">
                  <input type="text" id="exercise-search" class="input-field flex-1" placeholder="Search by name, muscle group, or category..." onkeyup="searchExercises(event)">
                  <button type="button" onclick="showAllExercises()" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                    Browse All
                  </button>
                </div>
                <div id="exercise-search-results" class="mt-2 max-h-60 overflow-y-auto"></div>
              </div>

              <!-- Selected Exercises List -->
              <div id="selected-exercises-list" class="space-y-2">
                ${workoutCreationState.exercises.length === 0 ? '<p class="text-neutral-600 text-sm">No exercises added yet. Search and add exercises above.</p>' : ''}
              </div>
            </div>

            <div class="flex gap-2 justify-end border-t pt-4">
              <button type="button" onclick="closeEnhancedWorkoutModal()" class="px-4 py-2 bg-neutral-200 text-neutral-700 rounded hover:bg-neutral-300 transition-colors">
                Cancel
              </button>
              <button type="submit" class="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors">
                ${isEdit ? 'Update' : 'Create'} Workout
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHtml);
  
  // Render existing exercises if editing
  if (workoutCreationState.exercises.length > 0) {
    renderSelectedExercises();
  }

  // Handle form submission
  document.getElementById('enhanced-workout-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const data = {
      name: formData.get('name'),
      description: formData.get('description') || '',
      difficulty: formData.get('difficulty'),
      duration_weeks: parseInt(formData.get('duration_weeks')) || null,
      category: formData.get('category') || null,
      created_by: state.trainer.id,
      exercises: workoutCreationState.exercises.map((ex, idx) => ({
        exercise_id: ex.exercise_id || ex.id,
        order: idx,
        sets: ex.sets,
        reps: ex.reps,
        duration_seconds: ex.duration_seconds,
        rest_seconds: ex.rest_seconds,
        weight: ex.weight,
        notes: ex.notes
      }))
    };

    try {
      if (isEdit) {
        await workoutAPI.updateTemplate(existingWorkout.id, data);
        showToast('Workout plan updated successfully!');
      } else {
        await workoutAPI.createTemplate(data);
        showToast('Workout plan created successfully!');
      }
      closeEnhancedWorkoutModal();
      loadWorkouts();
      document.getElementById('workout-form')?.reset();
    } catch (error) {
      console.error('Error saving workout plan:', error);
      showToast('Error saving workout plan: ' + (error.response?.data?.error || error.message));
    }
  });
}

window.closeEnhancedWorkoutModal = function() {
  const modal = document.getElementById('enhanced-workout-modal');
  if (modal) {
    modal.remove();
  }
  workoutCreationState.exercises = [];
  workoutCreationState.searchResults = [];
};

// Search exercises
window.searchExercises = function(event) {
  const searchTerm = event.target.value.toLowerCase().trim();
  const resultsContainer = document.getElementById('exercise-search-results');
  
  if (searchTerm.length < 2) {
    resultsContainer.innerHTML = '';
    return;
  }

  const results = workoutCreationState.availableExercises.filter(ex => 
    ex.name.toLowerCase().includes(searchTerm) ||
    (ex.muscle_group && ex.muscle_group.toLowerCase().includes(searchTerm)) ||
    (ex.category && ex.category.toLowerCase().includes(searchTerm))
  ).slice(0, 10);

  if (results.length === 0) {
    resultsContainer.innerHTML = '<p class="text-neutral-600 text-sm p-2">No exercises found</p>';
    return;
  }

  resultsContainer.innerHTML = `
    <div class="bg-white border rounded-lg shadow-lg divide-y max-h-80 overflow-y-auto">
      ${results.map(ex => `
        <div class="p-3 hover:bg-neutral-50 cursor-pointer" onclick="addExerciseToWorkout(${ex.id})">
          <div class="font-medium text-neutral-900">${ex.name}</div>
          <div class="text-xs text-neutral-600 mt-1">
            ${ex.muscle_group ? `<span class="capitalize">${ex.muscle_group}</span>` : ''}
            ${ex.category ? `<span class="ml-2 capitalize">${ex.category}</span>` : ''}
            ${ex.equipment ? `<span class="ml-2">${ex.equipment}</span>` : ''}
          </div>
        </div>
      `).join('')}
    </div>
  `;
};

window.showAllExercises = function() {
  const resultsContainer = document.getElementById('exercise-search-results');
  const exercises = workoutCreationState.availableExercises.slice(0, 20);
  
  if (exercises.length === 0) {
    resultsContainer.innerHTML = '<p class="text-neutral-600 text-sm p-2">No exercises available. Please add exercises to the system first.</p>';
    return;
  }
  
  resultsContainer.innerHTML = `
    <div class="bg-white border rounded-lg shadow-lg divide-y max-h-80 overflow-y-auto">
      ${exercises.map(ex => `
        <div class="p-3 hover:bg-neutral-50 cursor-pointer" onclick="addExerciseToWorkout(${ex.id})">
          <div class="font-medium text-neutral-900">${ex.name}</div>
          <div class="text-xs text-neutral-600 mt-1">
            ${ex.muscle_group ? `<span class="capitalize">${ex.muscle_group}</span>` : ''}
            ${ex.category ? `<span class="ml-2 capitalize">${ex.category}</span>` : ''}
            ${ex.equipment ? `<span class="ml-2">${ex.equipment}</span>` : ''}
          </div>
        </div>
      `).join('')}
    </div>
  `;
};

// Add exercise to workout
window.addExerciseToWorkout = function(exerciseId) {
  const exercise = workoutCreationState.availableExercises.find(ex => ex.id === exerciseId);
  if (!exercise) return;

  // Check if already added
  if (workoutCreationState.exercises.some(ex => (ex.exercise_id || ex.id) === exerciseId)) {
    showToast('Exercise already added');
    return;
  }

  workoutCreationState.exercises.push({
    exercise_id: exerciseId,
    name: exercise.name,
    muscle_group: exercise.muscle_group,
    sets: 3,
    reps: 10,
    duration_seconds: null,
    rest_seconds: 60,
    weight: null,
    notes: ''
  });

  renderSelectedExercises();
  document.getElementById('exercise-search-results').innerHTML = '';
  document.getElementById('exercise-search').value = '';
};

// Remove exercise from workout
window.removeExerciseFromWorkout = function(index) {
  workoutCreationState.exercises.splice(index, 1);
  renderSelectedExercises();
};

// Update exercise details
window.updateExerciseDetail = function(index, field, value) {
  if (workoutCreationState.exercises[index]) {
    workoutCreationState.exercises[index][field] = value;
  }
};

// Move exercise up/down
window.moveExercise = function(index, direction) {
  const newIndex = direction === 'up' ? index - 1 : index + 1;
  if (newIndex < 0 || newIndex >= workoutCreationState.exercises.length) return;
  
  const temp = workoutCreationState.exercises[index];
  workoutCreationState.exercises[index] = workoutCreationState.exercises[newIndex];
  workoutCreationState.exercises[newIndex] = temp;
  
  renderSelectedExercises();
};

// Render selected exercises
function renderSelectedExercises() {
  const container = document.getElementById('selected-exercises-list');
  
  if (workoutCreationState.exercises.length === 0) {
    container.innerHTML = '<p class="text-neutral-600 text-sm">No exercises added yet. Search and add exercises above.</p>';
    return;
  }

  container.innerHTML = workoutCreationState.exercises.map((ex, index) => `
    <div class="bg-neutral-50 border rounded-lg p-3">
      <div class="flex items-start justify-between mb-2">
        <div class="flex-1">
          <div class="font-medium text-neutral-900">${ex.name}</div>
          <div class="text-xs text-neutral-600">${ex.muscle_group ? `<span class="capitalize">${ex.muscle_group}</span>` : ''}</div>
        </div>
        <div class="flex gap-1">
          ${index > 0 ? `<button type="button" onclick="moveExercise(${index}, 'up')" class="p-1 text-neutral-600 hover:text-neutral-900" title="Move up">↑</button>` : ''}
          ${index < workoutCreationState.exercises.length - 1 ? `<button type="button" onclick="moveExercise(${index}, 'down')" class="p-1 text-neutral-600 hover:text-neutral-900" title="Move down">↓</button>` : ''}
          <button type="button" onclick="removeExerciseFromWorkout(${index})" class="p-1 text-red-600 hover:text-red-800" title="Remove">×</button>
        </div>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm">
        <div>
          <label class="text-xs text-neutral-600">Sets</label>
          <input type="number" value="${ex.sets || ''}" onchange="updateExerciseDetail(${index}, 'sets', parseInt(this.value) || null)" class="w-full px-2 py-1 border rounded" min="1">
        </div>
        <div>
          <label class="text-xs text-neutral-600">Reps</label>
          <input type="number" value="${ex.reps || ''}" onchange="updateExerciseDetail(${index}, 'reps', parseInt(this.value) || null)" class="w-full px-2 py-1 border rounded" min="1">
        </div>
        <div>
          <label class="text-xs text-neutral-600">Duration (sec)</label>
          <input type="number" value="${ex.duration_seconds || ''}" onchange="updateExerciseDetail(${index}, 'duration_seconds', parseInt(this.value) || null)" class="w-full px-2 py-1 border rounded" placeholder="Optional">
        </div>
        <div>
          <label class="text-xs text-neutral-600">Rest (sec)</label>
          <input type="number" value="${ex.rest_seconds || 60}" onchange="updateExerciseDetail(${index}, 'rest_seconds', parseInt(this.value) || 60)" class="w-full px-2 py-1 border rounded">
        </div>
        <div>
          <label class="text-xs text-neutral-600">Weight (lbs)</label>
          <input type="number" value="${ex.weight || ''}" onchange="updateExerciseDetail(${index}, 'weight', parseFloat(this.value) || null)" class="w-full px-2 py-1 border rounded" placeholder="Optional" step="0.5">
        </div>
      </div>
      <div class="mt-2">
        <label class="text-xs text-neutral-600">Notes</label>
        <input type="text" value="${ex.notes || ''}" onchange="updateExerciseDetail(${index}, 'notes', this.value)" class="w-full px-2 py-1 border rounded text-sm" placeholder="Optional notes...">
      </div>
    </div>
  `).join('');
}

// View workout details in a modal
window.viewWorkout = async function(workoutId) {
  try {
    // Fetch full workout details including exercises
    const response = await workoutAPI.getTemplate(workoutId);
    const workout = response.data || response;
    
    if (!workout) {
      showToast('Workout not found');
      return;
    }

    // Use the enhanced modal for editing
    showEnhancedWorkoutModal(workout);
  } catch (error) {
    console.error('Error viewing workout:', error);
    showToast('Error loading workout details: ' + (error.response?.data?.error || error.message));
  }
};

// Assign workout to client
window.assignWorkoutToClient = async function(workoutId) {
  try {
    const workout = state.workouts.find(w => w.id === workoutId);
    if (!workout) {
      showToast('Workout not found');
      return;
    }

    // Get trainer's clients
    const myClients = getMyClients();

    if (myClients.length === 0) {
      showToast('No clients assigned to you yet');
      return;
    }

    // Create modal to select client
    const modalHtml = `
      <div id="assign-workout-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-lg max-w-md w-full">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-2xl font-bold text-neutral-900">Assign Workout</h2>
              <button onclick="closeAssignWorkoutModal()" class="text-neutral-600 hover:text-neutral-900">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            <form id="assign-workout-form-modal" class="space-y-4">
              <div>
                <label class="form-label">Select Client *</label>
                <select name="client_id" required class="input-field">
                  <option value="">Choose a client...</option>
                  ${myClients.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
                </select>
              </div>
              <div>
                <label class="form-label">Start Date</label>
                <input type="date" name="start_date" class="input-field" value="${new Date().toISOString().split('T')[0]}">
              </div>
              <div>
                <label class="form-label">Notes</label>
                <textarea name="notes" class="input-field" rows="3" placeholder="Any special instructions..."></textarea>
              </div>
              <div class="flex gap-2 justify-end">
                <button type="button" onclick="closeAssignWorkoutModal()" class="px-4 py-2 bg-neutral-200 text-neutral-700 rounded hover:bg-neutral-300 transition-colors">
                  Cancel
                </button>
                <button type="submit" class="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors">
                  Assign Workout
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    `;

    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Handle form submission
    document.getElementById('assign-workout-form-modal').addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const data = {
        template_id: workoutId,
        client_id: parseInt(formData.get('client_id')),
        trainer_id: state.trainer.id,
        start_date: formData.get('start_date') || new Date().toISOString().split('T')[0],
        notes: formData.get('notes') || ''
      };

      try {
        await workoutAPI.assignWorkout(data);
        showToast('Workout assigned to client successfully!');
        closeAssignWorkoutModal();
      } catch (error) {
        console.error('Error assigning workout:', error);
        showToast('Error assigning workout: ' + (error.response?.data?.error || error.message));
      }
    });
  } catch (error) {
    console.error('Error assigning workout:', error);
    showToast('Error assigning workout');
  }
};

window.closeAssignWorkoutModal = function() {
  const modal = document.getElementById('assign-workout-modal');
  if (modal) {
    modal.remove();
  }
};

// Calendar functions
async function loadCalendar() {
  try {
    // Load clients for session scheduling
    const clientSelect = document.querySelector('#session-form select[name="client_id"]');
    const myClients = getMyClients();

    clientSelect.innerHTML = '<option value="">Choose a client...</option>' +
      myClients.map(c => `<option value="${c.id}">${c.name}</option>`).join('');

    // Load sessions
    const response = await sessionAPI.getAll({ trainer_id: state.trainer.id });
    state.sessions = response.data || [];

    const sessionsContainer = document.getElementById('sessions-list');
    
    if (state.sessions.length === 0) {
      sessionsContainer.innerHTML = '<p class="text-neutral-600">No sessions scheduled yet. Use the form to schedule a session!</p>';
      return;
    }

    // Display upcoming sessions
    const now = new Date();
    const upcomingSessions = state.sessions
      .filter(s => new Date(s.session_date) >= now)
      .sort((a, b) => new Date(a.session_date) - new Date(b.session_date));

    if (upcomingSessions.length === 0) {
      sessionsContainer.innerHTML = '<p class="text-neutral-600">No upcoming sessions. Use the form to schedule a session!</p>';
      return;
    }

    sessionsContainer.innerHTML = upcomingSessions.map(session => {
      const client = state.clients.find(c => c.id === session.client_id);
      const sessionDate = new Date(session.session_date);
      return `
        <div class="p-4 bg-neutral-50 rounded-lg">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h4 class="text-lg font-semibold text-neutral-900">${client?.name || 'Unknown Client'}</h4>
              <p class="text-sm text-neutral-600">${sessionDate.toLocaleDateString()} at ${sessionDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
              <p class="text-sm text-neutral-600">Duration: ${session.duration} minutes</p>
              <p class="text-sm text-orange-600 capitalize">${session.session_type}</p>
              ${session.notes ? `<p class="text-sm text-neutral-500 mt-2">${session.notes}</p>` : ''}
            </div>
          </div>
        </div>
      `;
    }).join('');
  } catch (error) {
    console.error('Error loading calendar:', error);
    const sessionsContainer = document.getElementById('sessions-list');
    sessionsContainer.innerHTML = '<p class="text-red-600">Error loading sessions. Please try again.</p>';
  }
}

// Messages functions
function loadMessages() {
  // Load clients for messaging
  const clientSelect = document.querySelector('#message-form select[name="client_id"]');
  const myAssignments = state.assignments.filter(a => a.trainer_id === state.trainer.id);
  const myClientIds = myAssignments.map(a => a.client_id);
  const myClients = state.clients.filter(c => myClientIds.includes(c.id));

  clientSelect.innerHTML = '<option value="">Choose a client...</option>' +
    myClients.map(c => `<option value="${c.id}">${c.name}</option>`).join('');

  // Mock messages
  const messagesContainer = document.getElementById('messages-list');
  messagesContainer.innerHTML = '<p class="text-neutral-600">No messages yet</p>';
}

// Challenges functions
function loadChallenges() {
  // Mock challenges
  const challengesContainer = document.getElementById('challenges-list');
  challengesContainer.innerHTML = '<p class="text-neutral-600">No challenges created yet. Use the form to create a challenge!</p>';
}

// Settings functions
async function loadSettings() {
  try {
    const user = auth.getUser();
    if (user) {
      document.getElementById('settings-email').textContent = user.email || 'N/A';
      document.getElementById('settings-role').textContent = user.role || 'Trainer';
      if (user.created_at) {
        document.getElementById('settings-member-since').textContent = new Date(user.created_at).toLocaleDateString();
      }
    }
  } catch (error) {
    console.error('Error loading settings:', error);
  }
}

// Form handlers - will be initialized in DOMContentLoaded
function initFormHandlers() {
  document.getElementById('assign-client-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
      trainer_id: state.trainer.id,
      client_id: parseInt(formData.get('client_id')),
      notes: formData.get('notes'),
    };

    try {
      await crmAPI.assignClientToTrainer(data);
      showToast('Client assigned successfully!');
      e.target.reset();
      loadClients();
      loadDashboard();
    } catch (error) {
      console.error('Error assigning client:', error);
      showToast('Error assigning client. Please try again.');
    }
  });

  document.getElementById('workout-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show enhanced workout creation modal
    showEnhancedWorkoutModal();
  });

  document.getElementById('session-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    // Validate required fields
    const clientId = parseInt(formData.get('client_id'));
    const sessionDate = formData.get('session_date');
    
    if (!clientId || isNaN(clientId)) {
      showToast('Please select a client');
      return;
    }
    
    if (!sessionDate) {
      showToast('Please select a date and time');
      return;
    }
    
    const data = {
      client_id: clientId,
      trainer_id: state.trainer.id,
      session_date: sessionDate,
      duration: parseInt(formData.get('duration')) || 60,
      session_type: formData.get('session_type'),
      status: 'scheduled',
      notes: formData.get('notes') || ''
    };

    try {
      await sessionAPI.create(data);
      showToast('Session scheduled successfully!');
      e.target.reset();
      loadCalendar();
    } catch (error) {
      console.error('Error scheduling session:', error);
      showToast('Error scheduling session: ' + (error.response?.data?.error || error.message));
    }
  });

  document.getElementById('message-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    showToast('Message sent! (Feature coming in next release)');
    e.target.reset();
  });

  document.getElementById('challenge-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    showToast('Challenge created! (Feature coming in next release)');
    e.target.reset();
  });

  document.getElementById('change-password-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const currentPassword = formData.get('current_password');
  const newPassword = formData.get('new_password');
  const confirmPassword = formData.get('confirm_password');

  // Validate passwords
  if (newPassword.length < 6) {
    showToast('New password must be at least 6 characters');
    return;
  }

  if (newPassword !== confirmPassword) {
    showToast('New passwords do not match');
    return;
  }

  try {
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
    const response = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${auth.getToken()}`
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    });

    const data = await response.json();

    if (response.ok) {
      showToast('Password changed successfully!');
      e.target.reset();
    } else {
      showToast(data.error || 'Failed to change password');
    }
  } catch (error) {
    console.error('Error changing password:', error);
    showToast('Error changing password. Please try again.');
  }
  });
}

// Initialize with auth check
document.addEventListener('DOMContentLoaded', async () => {
  // Require trainer role
  const isAuthorized = await requireRole(['trainer', 'admin']);
  if (!isAuthorized) {
    return; // requireRole redirects if not authorized
  }

  // Load the authenticated trainer's profile
  try {
    const response = await trainerAPI.getMe();
    state.trainer = response.data;
    state.trainerId = state.trainer.id;
    
    // Update top bar with trainer name
    const nameElement = document.querySelector('.top-bar .text-sm.font-semibold');
    if (nameElement && state.trainer.name) {
      nameElement.textContent = state.trainer.name;
    }
  } catch (error) {
    console.error('Error loading trainer profile:', error);
    showToast('Error loading your profile. Please try again.');
    // Fallback: try to get from user object
    const user = auth.getUser();
    if (user && user.id) {
      state.trainerId = user.id;
    }
  }

  initSidebar();
  initNavigation();
  initFormHandlers();
  
  // Restore last visited section or default to dashboard
  const lastSection = localStorage.getItem('currentSection');
  const lastSectionTitle = localStorage.getItem('currentSectionTitle');
  
  if (lastSection && document.getElementById(lastSection)) {
    // Restore the last section the user was on
    showSection(lastSection, lastSectionTitle || 'Dashboard');
    
    // Load data for that section
    switch(lastSection) {
      case 'dashboard-section':
        loadDashboard();
        break;
      case 'clients-section':
        loadClients();
        break;
      case 'workouts-section':
        loadWorkouts();
        break;
      case 'calendar-section':
        loadCalendar();
        break;
      case 'messages-section':
        loadMessages();
        break;
      case 'challenges-section':
        loadChallenges();
        break;
      case 'settings-section':
        loadSettings();
        break;
      default:
        loadDashboard();
    }
  } else {
    // Default to dashboard if no saved section
    showSection('dashboard-section', 'Dashboard');
    loadDashboard();
  }
});
