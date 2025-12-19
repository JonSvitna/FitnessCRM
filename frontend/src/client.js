import './styles/main.css';
import { trainerAPI, clientAPI, crmAPI } from './api.js';
import { requireRole, auth } from './auth.js';

// State management
let state = {
  client: { id: 1, name: 'Demo Client' }, // Mock client
  trainer: null,
  assignment: null,
  workouts: [],
  sessions: [],
  meals: [],
  progress: [],
  messages: [],
  sidebarExpanded: true,
};

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
}

// Navigation handlers - will be initialized in DOMContentLoaded
function initNavigation() {
  document.getElementById('nav-dashboard').addEventListener('click', () => {
    showSection('dashboard-section', 'Dashboard');
    loadDashboard();
  });

  document.getElementById('nav-profile').addEventListener('click', () => {
    showSection('profile-section', 'My Profile');
    loadProfile();
  });

  document.getElementById('nav-workouts').addEventListener('click', () => {
    showSection('workouts-section', 'Workouts');
    loadWorkouts();
  });

  document.getElementById('nav-calendar').addEventListener('click', () => {
    showSection('calendar-section', 'Calendar');
    loadCalendar();
  });

  document.getElementById('nav-meals').addEventListener('click', () => {
    showSection('meals-section', 'Nutrition');
    loadMeals();
  });

  document.getElementById('nav-progress').addEventListener('click', () => {
    showSection('progress-section', 'Progress');
    loadProgress();
  });

  document.getElementById('nav-messages').addEventListener('click', () => {
    showSection('messages-section', 'Messages');
    loadMessages();
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
    // Load assignment and trainer info
    const assignmentsResponse = await crmAPI.getAssignments();
    const assignments = assignmentsResponse.data;
    state.assignment = assignments.find(a => a.client_id === state.client.id);

    if (state.assignment) {
      const trainersResponse = await trainerAPI.getAll();
      state.trainer = trainersResponse.data.find(t => t.id === state.assignment.trainer_id);

      // Display trainer info
      const trainerContainer = document.getElementById('trainer-info');
      if (state.trainer) {
        trainerContainer.innerHTML = `
          <div class="flex items-start gap-4">
            <div class="w-16 h-16 bg-gradient-to-br from-orange-500 to-primary-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              ${state.trainer.name.charAt(0)}
            </div>
            <div>
              <h4 class="text-lg font-semibold text-neutral-900">${state.trainer.name}</h4>
              <p class="text-sm text-neutral-600">${state.trainer.email}</p>
              ${state.trainer.phone ? `<p class="text-sm text-neutral-600">${state.trainer.phone}</p>` : ''}
              ${state.trainer.specialization ? `<p class="text-sm text-orange-600 mt-2"><strong>Specialization:</strong> ${state.trainer.specialization}</p>` : ''}
              ${state.trainer.certification ? `<p class="text-sm text-neutral-600"><strong>Certification:</strong> ${state.trainer.certification}</p>` : ''}
            </div>
          </div>
        `;
      }
    } else {
      document.getElementById('trainer-info').innerHTML = '<p class="text-neutral-600">No trainer assigned yet</p>';
    }

    // Mock stats
    document.getElementById('workouts-completed').textContent = '0';
    document.getElementById('sessions-attended').textContent = '0';
    document.getElementById('days-active').textContent = '0';
    document.getElementById('new-messages').textContent = '0';

    // Mock upcoming sessions
    document.getElementById('upcoming-sessions').innerHTML = '<p class="text-neutral-600">No upcoming sessions</p>';
    
    // Mock today's workout
    document.getElementById('today-workout').innerHTML = '<p class="text-neutral-600">No workout assigned for today</p>';
  } catch (error) {
    console.error('Error loading dashboard:', error);
  }
}

// Profile functions
async function loadProfile() {
  try {
    const response = await clientAPI.get(state.client.id);
    const clientData = response.data;
    
    // Populate profile form
    const profileForm = document.getElementById('profile-form');
    profileForm.elements['name'].value = clientData.name || '';
    profileForm.elements['email'].value = clientData.email || '';
    profileForm.elements['phone'].value = clientData.phone || '';
    profileForm.elements['age'].value = clientData.age || '';

    // Populate fitness form
    const fitnessForm = document.getElementById('fitness-form');
    fitnessForm.elements['goals'].value = clientData.goals || '';
    fitnessForm.elements['medical_conditions'].value = clientData.medical_conditions || '';
    fitnessForm.elements['emergency_contact'].value = clientData.emergency_contact || '';
    fitnessForm.elements['emergency_phone'].value = clientData.emergency_phone || '';
  } catch (error) {
    console.error('Error loading profile:', error);
  }
}

// Workouts functions
function loadWorkouts() {
  // Mock workout plans
  const workoutsContainer = document.getElementById('workout-plans-list');
  workoutsContainer.innerHTML = '<p class="text-neutral-600">No workout plans assigned yet. Your trainer will assign workouts soon!</p>';

  // Mock workout history
  const historyContainer = document.getElementById('workout-history');
  historyContainer.innerHTML = '<p class="text-neutral-600">No workout history yet. Complete your first workout to see it here!</p>';
}

// Calendar functions
function loadCalendar() {
  // Mock sessions
  const sessionsContainer = document.getElementById('calendar-sessions');
  sessionsContainer.innerHTML = '<p class="text-neutral-600">No sessions scheduled yet</p>';
}

// Meals functions
function loadMeals() {
  // Mock meal plan
  const mealPlanContainer = document.getElementById('meal-plan');
  mealPlanContainer.innerHTML = '<p class="text-neutral-600">No meal plan assigned yet. Your trainer will create a plan for you!</p>';
}

// Progress functions
function loadProgress() {
  // Mock progress data
  document.getElementById('current-weight').textContent = '--';
  document.getElementById('current-body-fat').textContent = '--';
  document.getElementById('total-workouts').textContent = '0';
  document.getElementById('streak-days').textContent = '0';

  const historyContainer = document.getElementById('progress-history');
  historyContainer.innerHTML = '<p class="text-neutral-600">No progress records yet. Log your first progress entry!</p>';
}

// Messages functions
function loadMessages() {
  // Mock messages
  const messagesContainer = document.getElementById('messages-list');
  if (state.trainer) {
    messagesContainer.innerHTML = `
      <div class="text-center py-8">
        <p class="text-neutral-600 mb-4">Start a conversation with ${state.trainer.name}</p>
        <p class="text-sm text-neutral-500">Use the form on the left to send a message</p>
      </div>
    `;
  } else {
    messagesContainer.innerHTML = '<p class="text-neutral-600">No trainer assigned yet</p>';
  }
}

// Settings functions
async function loadSettings() {
  try {
    const user = auth.getUser();
    if (user) {
      document.getElementById('settings-email').textContent = user.email || 'N/A';
      document.getElementById('settings-role').textContent = user.role || 'Client';
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
  document.getElementById('profile-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    try {
      await clientAPI.update(state.client.id, data);
      showToast('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      showToast('Error updating profile. Please try again.');
    }
  });

  document.getElementById('fitness-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    try {
      await clientAPI.update(state.client.id, data);
      showToast('Fitness information updated successfully!');
    } catch (error) {
      console.error('Error updating fitness info:', error);
      showToast('Error updating information. Please try again.');
    }
  });

  document.getElementById('session-request-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    showToast('Session request sent! (Feature coming in next release)');
    e.target.reset();
  });

  document.getElementById('progress-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    showToast('Progress logged! (Feature coming in next release)');
    e.target.reset();
  });

  document.getElementById('message-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!state.trainer) {
      showToast('No trainer assigned yet');
      return;
    }
    showToast('Message sent! (Feature coming in next release)');
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
  // Require client/user role
  const isAuthorized = await requireRole(['client', 'user', 'admin']);
  if (!isAuthorized) {
    return; // requireRole redirects if not authorized
  }

  // Update client ID from auth user if available
  const user = auth.getUser();
  if (user && user.id) {
    state.client.id = user.id;
  }

  initSidebar();
  initNavigation();
  initFormHandlers();
  loadDashboard();
});
