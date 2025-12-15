import './styles/main.css';
import { trainerAPI, clientAPI, crmAPI, settingsAPI } from './api.js';

// State management
let state = {
  trainer: { id: 1, name: 'Demo Trainer' }, // Mock trainer
  clients: [],
  assignments: [],
  workouts: [],
  sessions: [],
  messages: [],
  challenges: [],
};

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

function showSection(sectionId) {
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

  // Update nav links
  const navButtons = document.querySelectorAll('.nav-link');
  navButtons.forEach(btn => btn.classList.remove('nav-link-active'));
  const activeNav = document.getElementById(`nav-${sectionId.replace('-section', '')}`);
  if (activeNav) {
    activeNav.classList.add('nav-link-active');
  }
}

// Navigation handlers
document.getElementById('nav-dashboard').addEventListener('click', () => {
  showSection('dashboard-section');
  loadDashboard();
});

document.getElementById('nav-clients').addEventListener('click', () => {
  showSection('clients-section');
  loadClients();
});

document.getElementById('nav-workouts').addEventListener('click', () => {
  showSection('workouts-section');
  loadWorkouts();
});

document.getElementById('nav-calendar').addEventListener('click', () => {
  showSection('calendar-section');
  loadCalendar();
});

document.getElementById('nav-messages').addEventListener('click', () => {
  showSection('messages-section');
  loadMessages();
});

document.getElementById('nav-challenges').addEventListener('click', () => {
  showSection('challenges-section');
  loadChallenges();
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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadDashboard();
});
