import './styles/main.css';
import { trainerAPI, clientAPI, crmAPI, settingsAPI } from './api.js';
import { requireRole, auth } from './auth.js';

// State management
let state = {
  trainer: { id: 1, name: 'Demo Trainer' }, // Mock trainer
  clients: [],
  assignments: [],
  workouts: [],
  sessions: [],
  messages: [],
  challenges: [],
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

// Navigation handlers
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

// Dashboard functions
async function loadDashboard() {
  try {
    const [clientsResponse, assignmentsResponse] = await Promise.all([
      clientAPI.getAll(),
      crmAPI.getAssignments(),
    ]);

    state.clients = clientsResponse.data;
    state.assignments = assignmentsResponse.data;

    // Filter my clients (assignments for this trainer)
    const myAssignments = state.assignments.filter(a => a.trainer_id === state.trainer.id);
    const myClientIds = myAssignments.map(a => a.client_id);
    const myClients = state.clients.filter(c => myClientIds.includes(c.id));
    const activeClients = myClients.filter(c => c.status === 'active');

    document.getElementById('total-clients').textContent = myClients.length;
    document.getElementById('active-clients').textContent = activeClients.length;
    document.getElementById('sessions-this-week').textContent = '0'; // TODO: Implement sessions
    document.getElementById('new-messages').textContent = '0'; // TODO: Implement messages

    // Today's schedule (mock data)
    const scheduleContainer = document.getElementById('today-schedule');
    scheduleContainer.innerHTML = '<p class="text-neutral-600">No sessions scheduled for today</p>';

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

// Workouts functions
function loadWorkouts() {
  // Mock workout plans
  const workoutsContainer = document.getElementById('workouts-list');
  workoutsContainer.innerHTML = '<p class="text-neutral-600">No workout plans created yet. Use the form to create your first plan!</p>';
}

// Calendar functions
function loadCalendar() {
  // Load clients for session scheduling
  const clientSelect = document.querySelector('#session-form select[name="client_id"]');
  const myAssignments = state.assignments.filter(a => a.trainer_id === state.trainer.id);
  const myClientIds = myAssignments.map(a => a.client_id);
  const myClients = state.clients.filter(c => myClientIds.includes(c.id));

  clientSelect.innerHTML = '<option value="">Choose a client...</option>' +
    myClients.map(c => `<option value="${c.id}">${c.name}</option>`).join('');

  // Mock sessions
  const sessionsContainer = document.getElementById('sessions-list');
  sessionsContainer.innerHTML = '<p class="text-neutral-600">No sessions scheduled yet. Use the form to schedule a session!</p>';
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

// Form handlers
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
  showToast('Workout plan created! (Feature coming in next release)');
  e.target.reset();
});

document.getElementById('session-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  showToast('Session scheduled! (Feature coming in next release)');
  e.target.reset();
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

// Initialize with auth check
document.addEventListener('DOMContentLoaded', async () => {
  // Require trainer role
  const isAuthorized = await requireRole(['trainer', 'admin']);
  if (!isAuthorized) {
    return; // requireRole redirects if not authorized
  }

  // Update trainer ID from auth user if available
  const user = auth.getUser();
  if (user && user.id) {
    state.trainer.id = user.id;
  }

  initSidebar();
  loadDashboard();
});
