import './styles/main.css';
import { trainerAPI, clientAPI, crmAPI, settingsAPI, activityAPI } from './api.js';

// State management
let state = {
  trainers: [],
  clients: [],
  assignments: [],
  settings: null,
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

document.getElementById('nav-trainers').addEventListener('click', () => {
  showSection('trainers-section');
  loadTrainers();
});

document.getElementById('nav-clients').addEventListener('click', () => {
  showSection('clients-section');
  loadClients();
});

document.getElementById('nav-management').addEventListener('click', () => {
  showSection('management-section');
  loadManagement();
});

document.getElementById('nav-settings').addEventListener('click', () => {
  showSection('settings-section');
  loadSettings();
});

// Trainer form handler
document.getElementById('trainer-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());

  try {
    const response = await trainerAPI.create(data);
    showToast('Trainer added successfully!');
    e.target.reset();
    loadTrainers();
    loadDashboard();
  } catch (error) {
    console.error('Error adding trainer:', error);
    showToast('Error adding trainer. Please try again.');
  }
});

// Client form handler
document.getElementById('client-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());

  try {
    const response = await clientAPI.create(data);
    showToast('Client added successfully!');
    e.target.reset();
    loadClients();
    loadDashboard();
  } catch (error) {
    console.error('Error adding client:', error);
    showToast('Error adding client. Please try again.');
  }
});

// Assignment form handler
document.getElementById('assignment-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());

  try {
    const response = await crmAPI.assignClientToTrainer(data);
    showToast('Assignment created successfully!');
    e.target.reset();
    loadAssignments();
    loadDashboard();
  } catch (error) {
    console.error('Error creating assignment:', error);
    showToast('Error creating assignment. Please try again.');
  }
});

// Load dashboard data
async function loadDashboard() {
  try {
    const [trainersResponse, clientsResponse, assignmentsResponse] = await Promise.all([
      trainerAPI.getAll(),
      clientAPI.getAll(),
      crmAPI.getAssignments(),
    ]);

    state.trainers = trainersResponse.data;
    state.clients = clientsResponse.data;
    state.assignments = assignmentsResponse.data;

    document.getElementById('total-trainers').textContent = state.trainers.length;
    document.getElementById('total-clients').textContent = state.clients.length;
    document.getElementById('total-assignments').textContent = state.assignments.length;

    // Load recent activity
    const activityContainer = document.getElementById('recent-activity');
    if (state.assignments.length > 0) {
      activityContainer.innerHTML = state.assignments.slice(0, 5).map(assignment => {
        const trainer = state.trainers.find(t => t.id === assignment.trainer_id);
        const client = state.clients.find(c => c.id === assignment.client_id);
        return `
          <div class="flex items-center justify-between p-3 bg-dark-tertiary rounded">
            <div>
              <p class="text-white">${client?.name || 'Unknown'} assigned to ${trainer?.name || 'Unknown'}</p>
              <p class="text-sm text-gray-400">${new Date(assignment.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        `;
      }).join('');
    } else {
      activityContainer.innerHTML = '<p class="text-gray-400">No recent activity</p>';
    }
  } catch (error) {
    console.error('Error loading dashboard:', error);
    showToast('Error loading dashboard data. Using demo mode.');
  }
}

// Load trainers
async function loadTrainers() {
  try {
    const response = await trainerAPI.getAll();
    state.trainers = response.data;
    renderTrainers();
  } catch (error) {
    console.error('Error loading trainers:', error);
    document.getElementById('trainers-list').innerHTML = '<p class="text-gray-400">Error loading trainers</p>';
  }
}

function renderTrainers() {
  const container = document.getElementById('trainers-list');
  if (state.trainers.length === 0) {
    container.innerHTML = '<p class="text-gray-400">No trainers added yet</p>';
    return;
  }

  container.innerHTML = state.trainers.map(trainer => `
    <div class="p-4 bg-dark-tertiary rounded-lg">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h4 class="text-lg font-semibold text-white">${trainer.name}</h4>
          <p class="text-sm text-gray-400">${trainer.email}</p>
          ${trainer.phone ? `<p class="text-sm text-gray-400">${trainer.phone}</p>` : ''}
          ${trainer.specialization ? `<p class="text-sm text-primary-400 mt-2">Specialization: ${trainer.specialization}</p>` : ''}
          ${trainer.certification ? `<p class="text-sm text-gray-400">Certification: ${trainer.certification}</p>` : ''}
          ${trainer.experience ? `<p class="text-sm text-gray-400">Experience: ${trainer.experience} years</p>` : ''}
        </div>
        <button onclick="deleteTrainer(${trainer.id})" class="text-red-400 hover:text-red-300 ml-4">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
        </button>
      </div>
    </div>
  `).join('');
}

// Load clients
async function loadClients() {
  try {
    const response = await clientAPI.getAll();
    state.clients = response.data;
    renderClients();
  } catch (error) {
    console.error('Error loading clients:', error);
    document.getElementById('clients-list').innerHTML = '<p class="text-gray-400">Error loading clients</p>';
  }
}

function renderClients() {
  const container = document.getElementById('clients-list');
  if (state.clients.length === 0) {
    container.innerHTML = '<p class="text-gray-400">No clients added yet</p>';
    return;
  }

  container.innerHTML = state.clients.map(client => `
    <div class="p-4 bg-dark-tertiary rounded-lg">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h4 class="text-lg font-semibold text-white">${client.name}</h4>
          <p class="text-sm text-gray-400">${client.email}</p>
          ${client.phone ? `<p class="text-sm text-gray-400">${client.phone}</p>` : ''}
          ${client.age ? `<p class="text-sm text-gray-400 mt-2">Age: ${client.age}</p>` : ''}
          ${client.goals ? `<p class="text-sm text-primary-400 mt-2">Goals: ${client.goals}</p>` : ''}
          ${client.medical_conditions ? `<p class="text-sm text-yellow-400">Medical: ${client.medical_conditions}</p>` : ''}
        </div>
        <button onclick="deleteClient(${client.id})" class="text-red-400 hover:text-red-300 ml-4">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
        </button>
      </div>
    </div>
  `).join('');
}

// Load management section
async function loadManagement() {
  await Promise.all([loadTrainers(), loadClients(), loadAssignments()]);
  updateAssignmentSelects();
}

function updateAssignmentSelects() {
  const trainerSelect = document.getElementById('assignment-trainer-select');
  const clientSelect = document.getElementById('assignment-client-select');

  trainerSelect.innerHTML = '<option value="">Choose a trainer...</option>' +
    state.trainers.map(t => `<option value="${t.id}">${t.name}</option>`).join('');

  clientSelect.innerHTML = '<option value="">Choose a client...</option>' +
    state.clients.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
}

async function loadAssignments() {
  try {
    const response = await crmAPI.getAssignments();
    state.assignments = response.data;
    renderAssignments();
  } catch (error) {
    console.error('Error loading assignments:', error);
    document.getElementById('assignments-list').innerHTML = '<p class="text-gray-400">Error loading assignments</p>';
  }
}

function renderAssignments() {
  const container = document.getElementById('assignments-list');
  if (state.assignments.length === 0) {
    container.innerHTML = '<p class="text-gray-400">No assignments yet</p>';
    return;
  }

  container.innerHTML = state.assignments.map(assignment => {
    const trainer = state.trainers.find(t => t.id === assignment.trainer_id);
    const client = state.clients.find(c => c.id === assignment.client_id);
    return `
      <div class="p-4 bg-dark-tertiary rounded-lg">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h4 class="text-lg font-semibold text-white">Assignment #${assignment.id}</h4>
            <div class="mt-2 space-y-1">
              <p class="text-sm text-gray-300">
                <span class="text-primary-400">Trainer:</span> ${trainer?.name || 'Unknown'}
              </p>
              <p class="text-sm text-gray-300">
                <span class="text-primary-400">Client:</span> ${client?.name || 'Unknown'}
              </p>
              ${assignment.notes ? `<p class="text-sm text-gray-400 mt-2">${assignment.notes}</p>` : ''}
              <p class="text-xs text-gray-500 mt-2">Created: ${new Date(assignment.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Settings functions
async function loadSettings() {
  try {
    const response = await settingsAPI.get();
    state.settings = response.data;
    populateSettingsForms();
    loadActivityLog();
  } catch (error) {
    console.error('Error loading settings:', error);
    // If no settings exist, that's okay - forms will be empty
    loadActivityLog();
  }
}

function populateSettingsForms() {
  if (!state.settings) return;
  
  // Business profile form
  const businessForm = document.getElementById('business-profile-form');
  if (businessForm && state.settings) {
    businessForm.elements['business_name'].value = state.settings.business_name || '';
    businessForm.elements['owner_name'].value = state.settings.owner_name || '';
    businessForm.elements['contact_email'].value = state.settings.contact_email || '';
    businessForm.elements['contact_phone'].value = state.settings.contact_phone || '';
    businessForm.elements['address'].value = state.settings.address || '';
    businessForm.elements['website'].value = state.settings.website || '';
  }
  
  // SendGrid form
  const sendgridForm = document.getElementById('sendgrid-form');
  if (sendgridForm && state.settings) {
    sendgridForm.elements['sendgrid_from_email'].value = state.settings.sendgrid_from_email || '';
    sendgridForm.elements['sendgrid_from_name'].value = state.settings.sendgrid_from_name || '';
    sendgridForm.elements['sendgrid_enabled'].checked = state.settings.sendgrid_enabled || false;
  }
  
  // Twilio form
  const twilioForm = document.getElementById('twilio-form');
  if (twilioForm && state.settings) {
    twilioForm.elements['twilio_phone_number'].value = state.settings.twilio_phone_number || '';
    twilioForm.elements['twilio_enabled'].checked = state.settings.twilio_enabled || false;
  }
}

async function loadActivityLog() {
  try {
    const response = await activityAPI.getRecent(20);
    const activities = response.data.activities;
    
    const container = document.getElementById('activity-log');
    if (activities.length === 0) {
      container.innerHTML = '<p class="text-gray-400">No activity yet</p>';
      return;
    }
    
    container.innerHTML = activities.map(activity => `
      <div class="flex items-start justify-between p-2 bg-white hover:bg-neutral-100 rounded border-l-4 ${
        activity.action === 'create' ? 'border-green-500' :
        activity.action === 'update' ? 'border-blue-500' :
        activity.action === 'delete' ? 'border-red-500' :
        'border-gray-500'
      }">
        <div class="flex-1">
          <p class="text-sm font-medium text-neutral-900">
            ${activity.action.toUpperCase()} ${activity.entity_type}
            ${activity.entity_id ? `#${activity.entity_id}` : ''}
          </p>
          ${activity.user_identifier ? `<p class="text-xs text-neutral-600">${activity.user_identifier}</p>` : ''}
          <p class="text-xs text-neutral-500">${new Date(activity.created_at).toLocaleString()}</p>
        </div>
      </div>
    `).join('');
  } catch (error) {
    console.error('Error loading activity log:', error);
    document.getElementById('activity-log').innerHTML = '<p class="text-gray-400">Error loading activity log</p>';
  }
}

// Settings form handlers
document.getElementById('business-profile-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  
  try {
    await settingsAPI.update(data);
    showToast('Business profile updated successfully!');
    loadSettings();
  } catch (error) {
    console.error('Error updating business profile:', error);
    showToast('Error updating business profile. Please try again.');
  }
});

document.getElementById('sendgrid-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  data.sendgrid_enabled = e.target.elements['sendgrid_enabled'].checked;
  
  try {
    await settingsAPI.update(data);
    showToast('SendGrid settings updated successfully!');
    loadSettings();
  } catch (error) {
    console.error('Error updating SendGrid settings:', error);
    showToast('Error updating SendGrid settings. Please try again.');
  }
});

document.getElementById('twilio-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  data.twilio_enabled = e.target.elements['twilio_enabled'].checked;
  
  try {
    await settingsAPI.update(data);
    showToast('Twilio settings updated successfully!');
    loadSettings();
  } catch (error) {
    console.error('Error updating Twilio settings:', error);
    showToast('Error updating Twilio settings. Please try again.');
  }
});

document.getElementById('test-sendgrid-btn').addEventListener('click', async () => {
  try {
    await settingsAPI.testSendGrid();
    showToast('SendGrid connection successful!');
  } catch (error) {
    console.error('Error testing SendGrid:', error);
    showToast('SendGrid connection failed. Check your settings.');
  }
});

document.getElementById('test-twilio-btn').addEventListener('click', async () => {
  try {
    await settingsAPI.testTwilio();
    showToast('Twilio connection successful!');
  } catch (error) {
    console.error('Error testing Twilio:', error);
    showToast('Twilio connection failed. Check your settings.');
  }
});

// Delete functions (global scope for inline onclick handlers)
window.deleteTrainer = async function(id) {
  if (!confirm('Are you sure you want to delete this trainer?')) return;
  
  try {
    await trainerAPI.delete(id);
    showToast('Trainer deleted successfully');
    loadTrainers();
    loadDashboard();
  } catch (error) {
    console.error('Error deleting trainer:', error);
    showToast('Error deleting trainer');
  }
};

window.deleteClient = async function(id) {
  if (!confirm('Are you sure you want to delete this client?')) return;
  
  try {
    await clientAPI.delete(id);
    showToast('Client deleted successfully');
    loadClients();
    loadDashboard();
  } catch (error) {
    console.error('Error deleting client:', error);
    showToast('Error deleting client');
  }
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  loadDashboard();
});
