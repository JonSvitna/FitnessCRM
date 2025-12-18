import './styles/main.css';
import { trainerAPI, clientAPI, crmAPI, settingsAPI, activityAPI, sessionAPI, recurringSessionAPI, measurementAPI, fileAPI, exerciseAPI, workoutAPI, progressPhotoAPI, goalAPI } from './api.js';
import { initCollapsibleSections } from './sidebar-sections.js';
import './pwa.js';
import './offline.js';
import './mobile.js';
import Chart from 'chart.js/auto';

// State management
let state = {
  trainers: [],
  clients: [],
  assignments: [],
  sessions: [],
  measurements: [],
  files: [],
  exercises: [],
  workoutTemplates: [],
  clientAssignments: [],
  progressPhotos: [],
  goals: [],
  settings: null,
  trainersPagination: { page: 1, per_page: 25, total: 0, pages: 0 },
  clientsPagination: { page: 1, per_page: 25, total: 0, pages: 0 },
  filesPagination: { page: 1, per_page: 25, total: 0, pages: 0 },
  sidebarExpanded: true,
  selectedProgressClient: null,
  selectedFilesClient: null,
  selectedAssignmentClient: null,
  currentWorkoutTab: 'exercises',
  templateExercises: [], // Exercises being added to current template
  charts: {
    weight: null,
    bodyComposition: null,
    circumferences: null,
    vitals: null
  }
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

  // Desktop sidebar toggle
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

      // Update collapse icon
      if (collapseIcon) {
        if (state.sidebarExpanded) {
          collapseIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"></path>';
        } else {
          collapseIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path>';
        }
      }
    });
  }

  // Mobile menu toggle
  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('sidebar-mobile-open');
      if (mobileOverlay) {
        mobileOverlay.classList.toggle('hidden');
      }
    });
  }

  // Mobile overlay close
  if (mobileOverlay) {
    mobileOverlay.addEventListener('click', () => {
      sidebar.classList.remove('sidebar-mobile-open');
      mobileOverlay.classList.add('hidden');
    });
  }
}

// Update showSection to also update page title and close mobile menu
function updatePageTitle(title) {
  const pageTitle = document.getElementById('page-title');
  if (pageTitle) {
    pageTitle.textContent = title;
  }
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

function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
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

  // Update sidebar navigation
  const sidebarItems = document.querySelectorAll('.sidebar-item');
  sidebarItems.forEach(item => item.classList.remove('sidebar-item-active'));
  const activeNav = document.getElementById(`nav-${sectionId.replace('-section', '')}`);
  if (activeNav) {
    activeNav.classList.add('sidebar-item-active');
  }

  // Update page title
  if (title) {
    updatePageTitle(title);
  }

  // Close mobile menu
  closeMobileMenu();
}

// Navigation handlers
document.getElementById('nav-dashboard').addEventListener('click', () => {
  showSection('dashboard-section', 'Dashboard');
  loadDashboard();
});

document.getElementById('nav-trainers').addEventListener('click', () => {
  showSection('trainers-section', 'Trainers');
  loadTrainers();
});

document.getElementById('nav-clients').addEventListener('click', () => {
  showSection('clients-section', 'Clients');
  loadClients();
});

document.getElementById('nav-management').addEventListener('click', () => {
  showSection('management-section', 'Assignments');
  loadManagement();
});

document.getElementById('nav-calendar').addEventListener('click', () => {
  showSection('calendar-section', 'Calendar');
  loadCalendar();
});

document.getElementById('nav-progress').addEventListener('click', () => {
  showSection('progress-section', 'Progress Tracking');
  loadProgressSection();
});

document.getElementById('nav-files').addEventListener('click', () => {
  showSection('files-section', 'File Management');
  loadFilesSection();
});

document.getElementById('nav-workouts').addEventListener('click', () => {
  showSection('workouts-section', 'Workout Management');
  loadWorkoutsSection();
});

document.getElementById('nav-activity').addEventListener('click', () => {
  showSection('activity-section', 'Activity Log');
  loadActivityLog();
});

document.getElementById('nav-settings').addEventListener('click', () => {
  showSection('settings-section', 'Settings');
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
      trainerAPI.getAll({ per_page: 1000 }),
      clientAPI.getAll({ per_page: 1000 }),
      crmAPI.getAssignments(),
    ]);

    // Handle both paginated and non-paginated responses
    state.trainers = Array.isArray(trainersResponse.data) ? trainersResponse.data : (trainersResponse.data.items || []);
    state.clients = Array.isArray(clientsResponse.data) ? clientsResponse.data : (clientsResponse.data.items || []);
    state.assignments = assignmentsResponse.data;

    document.getElementById('total-trainers').textContent = Array.isArray(trainersResponse.data) ? trainersResponse.data.length : (trainersResponse.data.total || 0);
    document.getElementById('total-clients').textContent = Array.isArray(clientsResponse.data) ? clientsResponse.data.length : (clientsResponse.data.total || 0);
    document.getElementById('total-assignments').textContent = state.assignments.length;

    // Load recent activity
    const activityContainer = document.getElementById('recent-activity');
    if (state.assignments.length > 0) {
      // Handle both array and paginated object responses
      const trainers = Array.isArray(state.trainers) ? state.trainers : (state.trainers.items || []);
      const clients = Array.isArray(state.clients) ? state.clients : (state.clients.items || []);
      
      activityContainer.innerHTML = state.assignments.slice(0, 5).map(assignment => {
        const trainer = trainers.find(t => t.id === assignment.trainer_id);
        const client = clients.find(c => c.id === assignment.client_id);
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

// Load trainers with optional search and filter
async function loadTrainers(searchParams = {}) {
  try {
    const params = {
      ...searchParams,
      page: state.trainersPagination.page,
      per_page: state.trainersPagination.per_page
    };
    const response = await trainerAPI.getAll(params);
    
    // Handle both old format (array) and new format (paginated object)
    if (Array.isArray(response.data)) {
      state.trainers = response.data;
      state.trainersPagination.total = response.data.length;
    } else {
      state.trainers = response.data.items || [];
      state.trainersPagination = {
        ...state.trainersPagination,
        total: response.data.total,
        pages: response.data.pages,
        page: response.data.page
      };
    }
    
    renderTrainers();
    updateTrainersPaginationUI();
  } catch (error) {
    console.error('Error loading trainers:', error);
    document.getElementById('trainers-list').innerHTML = '<p class="text-gray-400">Error loading trainers</p>';
  }
}

function updateTrainersPaginationUI() {
  const paginationDiv = document.getElementById('trainers-pagination');
  const { page, per_page, total, pages } = state.trainersPagination;
  
  if (total === 0) {
    paginationDiv?.classList.add('hidden');
    return;
  }
  
  paginationDiv?.classList.remove('hidden');
  
  const start = (page - 1) * per_page + 1;
  const end = Math.min(page * per_page, total);
  
  document.getElementById('trainers-showing').textContent = `${start}-${end}`;
  document.getElementById('trainers-total').textContent = total;
  document.getElementById('trainers-page-info').textContent = `Page ${page} of ${pages}`;
  
  const prevBtn = document.getElementById('trainers-prev');
  const nextBtn = document.getElementById('trainers-next');
  
  if (prevBtn) prevBtn.disabled = page <= 1;
  if (nextBtn) nextBtn.disabled = page >= pages;
}

// Trainer search and filter handlers
document.getElementById('trainer-search')?.addEventListener('input', (e) => {
  const search = e.target.value;
  const specialization = document.getElementById('trainer-specialization-filter').value;
  loadTrainers({ search, specialization });
});

document.getElementById('trainer-specialization-filter')?.addEventListener('change', (e) => {
  const specialization = e.target.value;
  const search = document.getElementById('trainer-search').value;
  loadTrainers({ search, specialization });
});

document.getElementById('trainer-clear-filters')?.addEventListener('click', () => {
  document.getElementById('trainer-search').value = '';
  document.getElementById('trainer-specialization-filter').value = '';
  state.trainersPagination.page = 1;
  loadTrainers();
});

document.getElementById('trainer-export-csv')?.addEventListener('click', async () => {
  try {
    // Get all trainers without pagination
    const response = await trainerAPI.getAll({ per_page: 1000 });
    const trainers = response.data.items || response.data;
    
    if (!trainers || trainers.length === 0) {
      showToast('No trainers to export');
      return;
    }
    
    exportToCSV(trainers, 'trainers');
    showToast('Trainers exported successfully!');
  } catch (error) {
    console.error('Error exporting trainers:', error);
    showToast('Error exporting trainers');
  }
});

// Trainer pagination handlers
document.getElementById('trainers-per-page')?.addEventListener('change', (e) => {
  state.trainersPagination.per_page = parseInt(e.target.value);
  state.trainersPagination.page = 1;
  const search = document.getElementById('trainer-search').value;
  const specialization = document.getElementById('trainer-specialization-filter').value;
  loadTrainers({ search, specialization });
});

document.getElementById('trainers-prev')?.addEventListener('click', () => {
  if (state.trainersPagination.page > 1) {
    state.trainersPagination.page--;
    const search = document.getElementById('trainer-search').value;
    const specialization = document.getElementById('trainer-specialization-filter').value;
    loadTrainers({ search, specialization });
  }
});

document.getElementById('trainers-next')?.addEventListener('click', () => {
  if (state.trainersPagination.page < state.trainersPagination.pages) {
    state.trainersPagination.page++;
    const search = document.getElementById('trainer-search').value;
    const specialization = document.getElementById('trainer-specialization-filter').value;
    loadTrainers({ search, specialization });
  }
});

function renderTrainers() {
  const container = document.getElementById('trainers-list');
  // Handle both array and paginated object responses
  const trainers = Array.isArray(state.trainers) ? state.trainers : (state.trainers.items || []);
  
  if (trainers.length === 0) {
    container.innerHTML = '<p class="text-gray-400">No trainers added yet</p>';
    return;
  }

  container.innerHTML = trainers.map(trainer => `
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

// Load clients with optional search and filter
async function loadClients(searchParams = {}) {
  try {
    const params = {
      ...searchParams,
      page: state.clientsPagination.page,
      per_page: state.clientsPagination.per_page
    };
    const response = await clientAPI.getAll(params);
    
    // Handle both old format (array) and new format (paginated object)
    if (Array.isArray(response.data)) {
      state.clients = response.data;
      state.clientsPagination.total = response.data.length;
    } else {
      state.clients = response.data.items || [];
      state.clientsPagination = {
        ...state.clientsPagination,
        total: response.data.total,
        pages: response.data.pages,
        page: response.data.page
      };
    }
    
    renderClients();
    updateClientsPaginationUI();
  } catch (error) {
    console.error('Error loading clients:', error);
    document.getElementById('clients-list').innerHTML = '<p class="text-gray-400">Error loading clients</p>';
  }
}

function updateClientsPaginationUI() {
  const paginationDiv = document.getElementById('clients-pagination');
  const { page, per_page, total, pages } = state.clientsPagination;
  
  if (total === 0) {
    paginationDiv?.classList.add('hidden');
    return;
  }
  
  paginationDiv?.classList.remove('hidden');
  
  const start = (page - 1) * per_page + 1;
  const end = Math.min(page * per_page, total);
  
  document.getElementById('clients-showing').textContent = `${start}-${end}`;
  document.getElementById('clients-total').textContent = total;
  document.getElementById('clients-page-info').textContent = `Page ${page} of ${pages}`;
  
  const prevBtn = document.getElementById('clients-prev');
  const nextBtn = document.getElementById('clients-next');
  
  if (prevBtn) prevBtn.disabled = page <= 1;
  if (nextBtn) nextBtn.disabled = page >= pages;
}


document.getElementById('client-export-csv')?.addEventListener('click', async () => {
  try {
    // Get all clients without pagination
    const response = await clientAPI.getAll({ per_page: 1000 });
    const clients = response.data.items || response.data;
    
    if (!clients || clients.length === 0) {
      showToast('No clients to export');
      return;
    }
    
    exportToCSV(clients, 'clients');
    showToast('Clients exported successfully!');
  } catch (error) {
    console.error('Error exporting clients:', error);
    showToast('Error exporting clients');
  }
});
// Client search and filter handlers
document.getElementById('client-search')?.addEventListener('input', (e) => {
  const search = e.target.value;
  const status = document.getElementById('client-status-filter').value;
  loadClients({ search, status });
});

document.getElementById('client-status-filter')?.addEventListener('change', (e) => {
  const status = e.target.value;
  const search = document.getElementById('client-search').value;
  loadClients({ search, status });
});

document.getElementById('client-clear-filters')?.addEventListener('click', () => {
  document.getElementById('client-search').value = '';
  document.getElementById('client-status-filter').value = '';
  state.clientsPagination.page = 1;
  loadClients();
});

// Client pagination handlers
document.getElementById('clients-per-page')?.addEventListener('change', (e) => {
  state.clientsPagination.per_page = parseInt(e.target.value);
  state.clientsPagination.page = 1;
  const search = document.getElementById('client-search').value;
  const status = document.getElementById('client-status-filter').value;
  loadClients({ search, status });
});

document.getElementById('clients-prev')?.addEventListener('click', () => {
  if (state.clientsPagination.page > 1) {
    state.clientsPagination.page--;
    const search = document.getElementById('client-search').value;
    const status = document.getElementById('client-status-filter').value;
    loadClients({ search, status });
  }
});

document.getElementById('clients-next')?.addEventListener('click', () => {
  if (state.clientsPagination.page < state.clientsPagination.pages) {
    state.clientsPagination.page++;
    const search = document.getElementById('client-search').value;
    const status = document.getElementById('client-status-filter').value;
    loadClients({ search, status });
  }
});

function renderClients() {
  const container = document.getElementById('clients-list');
  // Handle both array and paginated object responses
  const clients = Array.isArray(state.clients) ? state.clients : (state.clients.items || []);
  
  if (clients.length === 0) {
    container.innerHTML = '<p class="text-gray-400">No clients added yet</p>';
    return;
  }

  container.innerHTML = clients.map(client => `
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
  // Load all trainers and clients for management view (no pagination)
  await Promise.all([
    loadTrainers({ per_page: 1000 }),
    loadClients({ per_page: 1000 }),
    loadAssignments()
  ]);
  updateAssignmentSelects();
}

function updateAssignmentSelects() {
  const trainerSelect = document.getElementById('assignment-trainer-select');
  const clientSelect = document.getElementById('assignment-client-select');

  // Handle both array and paginated object responses
  const trainers = Array.isArray(state.trainers) ? state.trainers : (state.trainers.items || []);
  const clients = Array.isArray(state.clients) ? state.clients : (state.clients.items || []);

  trainerSelect.innerHTML = '<option value="">Choose a trainer...</option>' +
    trainers.map(t => `<option value="${t.id}">${t.name}</option>`).join('');

  clientSelect.innerHTML = '<option value="">Choose a client...</option>' +
    clients.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
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

  // Handle both array and paginated object responses
  const trainers = Array.isArray(state.trainers) ? state.trainers : (state.trainers.items || []);
  const clients = Array.isArray(state.clients) ? state.clients : (state.clients.items || []);

  container.innerHTML = state.assignments.map(assignment => {
    const trainer = trainers.find(t => t.id === assignment.trainer_id);
    const client = clients.find(c => c.id === assignment.client_id);
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

// Activity Log functions
async function loadActivityLog() {
  try {
    const [activitiesResponse, statsResponse] = await Promise.all([
      activityAPI.getRecent(100),
      activityAPI.getStats()
    ]);
    
    renderActivityLog(activitiesResponse.data.activities);
    renderActivityStats(statsResponse.data);
  } catch (error) {
    console.error('Error loading activity log:', error);
    document.getElementById('activity-list').innerHTML = '<p class="text-gray-400">Error loading activities</p>';
  }
}

function renderActivityLog(activities) {
  const container = document.getElementById('activity-list');
  
  if (!activities || activities.length === 0) {
    container.innerHTML = '<p class="text-gray-400">No activities yet</p>';
    return;
  }
  
  container.innerHTML = activities.map(activity => {
    const date = new Date(activity.timestamp);
    const actionColor = {
      create: 'text-green-400',
      update: 'text-blue-400',
      delete: 'text-red-400',
      view: 'text-gray-400'
    }[activity.action] || 'text-gray-400';
    
    const actionIcon = {
      create: '✨',
      update: '✏️',
      delete: '🗑️',
      view: '👁️'
    }[activity.action] || '•';
    
    return `
      <div class="p-3 bg-dark-tertiary rounded-lg hover:bg-opacity-80 transition-colors">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <span class="text-lg">${actionIcon}</span>
              <span class="${actionColor} font-semibold capitalize">${activity.action}</span>
              <span class="text-gray-400">·</span>
              <span class="text-primary-400 capitalize">${activity.entity_type}</span>
              ${activity.entity_id ? `<span class="text-gray-500">#${activity.entity_id}</span>` : ''}
            </div>
            ${activity.details ? `<p class="text-sm text-gray-400 mt-1">${JSON.stringify(activity.details)}</p>` : ''}
            ${activity.user_identifier ? `<p class="text-xs text-gray-500 mt-1">by ${activity.user_identifier}</p>` : ''}
          </div>
          <span class="text-xs text-gray-500">${date.toLocaleString()}</span>
        </div>
      </div>
    `;
  }).join('');
}

function renderActivityStats(stats) {
  document.getElementById('activity-total').textContent = stats.total_activities || 0;
  
  // Calculate today and this week (simplified)
  document.getElementById('activity-today').textContent = '-';
  document.getElementById('activity-week').textContent = '-';
}

// Activity filter handlers
document.getElementById('activity-type-filter')?.addEventListener('change', async (e) => {
  const type = e.target.value;
  const entity = document.getElementById('activity-entity-filter').value;
  try {
    const response = await activityAPI.getAll({ action: type, entity_type: entity });
    renderActivityLog(response.data.activities);
  } catch (error) {
    console.error('Error filtering activities:', error);
  }
});

document.getElementById('activity-entity-filter')?.addEventListener('change', async (e) => {
  const entity = e.target.value;
  const type = document.getElementById('activity-type-filter').value;
  try {
    const response = await activityAPI.getAll({ action: type, entity_type: entity });
    renderActivityLog(response.data.activities);
  } catch (error) {
    console.error('Error filtering activities:', error);
  }
});

document.getElementById('activity-clear-filters')?.addEventListener('click', () => {
  document.getElementById('activity-type-filter').value = '';
  document.getElementById('activity-entity-filter').value = '';
  loadActivityLog();
});

document.getElementById('activity-export-csv')?.addEventListener('click', async () => {
  try {
    const response = await activityAPI.getRecent(1000);
    const activities = response.data.activities;
    
    if (!activities || activities.length === 0) {
      showToast('No activities to export');
      return;
    }
    
    exportToCSV(activities, 'activity-log');
    showToast('Activity log exported successfully!');
  } catch (error) {
    console.error('Error exporting activities:', error);
    showToast('Error exporting activities');
  }
});

// Export to CSV utility function
function exportToCSV(data, filename) {
  if (!data || data.length === 0) return;
  
  // Get headers from first object
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  let csv = headers.join(',') + '\n';
  
  data.forEach(row => {
    const values = headers.map(header => {
      const value = row[header];
      // Handle special characters and wrap in quotes
      if (value === null || value === undefined) return '';
      const stringValue = typeof value === 'object' ? JSON.stringify(value) : String(value);
      return '"' + stringValue.replace(/"/g, '""') + '"';
    });
    csv += values.join(',') + '\n';
  });
  
  // Create download link
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}-${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

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

// Calendar state
let calendarState = {
  currentDate: new Date(),
  selectedDate: null,
  filterTrainer: null,
  filterClient: null,
  filterStatus: null
};

// Calendar functions
async function loadCalendar() {
  // Load trainers and clients for filters
  await Promise.all([loadTrainers({ per_page: 1000 }), loadClients({ per_page: 1000 })]);
  
  // Populate filter dropdowns
  populateCalendarFilters();
  
  // Render calendar
  renderCalendar();
  
  // Load sessions for current month
  await loadSessions();
  
  // Setup calendar controls
  setupCalendarControls();
}

function populateCalendarFilters() {
  const trainerFilter = document.getElementById('calendar-trainer-filter');
  const clientFilter = document.getElementById('calendar-client-filter');
  
  const trainers = Array.isArray(state.trainers) ? state.trainers : (state.trainers.items || []);
  const clients = Array.isArray(state.clients) ? state.clients : (state.clients.items || []);
  
  trainerFilter.innerHTML = '<option value="">All Trainers</option>' +
    trainers.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
  
  clientFilter.innerHTML = '<option value="">All Clients</option>' +
    clients.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
}

function setupCalendarControls() {
  // Month navigation
  document.getElementById('prev-month').addEventListener('click', () => {
    calendarState.currentDate.setMonth(calendarState.currentDate.getMonth() - 1);
    renderCalendar();
    loadSessions();
  });
  
  document.getElementById('next-month').addEventListener('click', () => {
    calendarState.currentDate.setMonth(calendarState.currentDate.getMonth() + 1);
    renderCalendar();
    loadSessions();
  });
  
  document.getElementById('today-btn').addEventListener('click', () => {
    calendarState.currentDate = new Date();
    renderCalendar();
    loadSessions();
  });
  
  // Filters
  document.getElementById('calendar-trainer-filter').addEventListener('change', (e) => {
    calendarState.filterTrainer = e.target.value || null;
    loadSessions();
  });
  
  document.getElementById('calendar-client-filter').addEventListener('change', (e) => {
    calendarState.filterClient = e.target.value || null;
    loadSessions();
  });
  
  document.getElementById('calendar-status-filter').addEventListener('change', (e) => {
    calendarState.filterStatus = e.target.value || null;
    loadSessions();
  });
  
  // Create session button
  document.getElementById('create-session-btn').addEventListener('click', () => {
    openSessionModal();
  });
  
  // Export calendar button
  document.getElementById('export-calendar-btn').addEventListener('click', () => {
    const year = calendarState.currentDate.getFullYear();
    const month = calendarState.currentDate.getMonth();
    const startDate = new Date(year, month, 1);
    const endDate = new Date(year, month + 1, 0, 23, 59, 59);
    
    const params = {
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString()
    };
    
    if (calendarState.filterTrainer) params.trainer_id = calendarState.filterTrainer;
    if (calendarState.filterClient) params.client_id = calendarState.filterClient;
    
    sessionAPI.exportIcal(params);
    showToast('Downloading calendar file...');
  });
  
  // Modal controls
  document.getElementById('close-session-modal').addEventListener('click', closeSessionModal);
  document.getElementById('cancel-session-btn').addEventListener('click', closeSessionModal);
  
  // Session form
  document.getElementById('session-form').addEventListener('submit', handleSessionSubmit);
  
  // Recurring session toggle
  document.getElementById('session-recurring').addEventListener('change', (e) => {
    const recurringOptions = document.getElementById('recurring-options');
    if (e.target.checked) {
      recurringOptions.classList.remove('hidden');
    } else {
      recurringOptions.classList.add('hidden');
    }
  });
  
  // Set default recurrence day based on selected date
  document.getElementById('session-date').addEventListener('change', (e) => {
    if (document.getElementById('session-recurring').checked) {
      const selectedDate = new Date(e.target.value);
      const dayOfWeek = selectedDate.getDay();
      // Auto-check the day of week for the selected date
      document.querySelectorAll('input[name="recurrence_days"]').forEach(checkbox => {
        checkbox.checked = parseInt(checkbox.value) === dayOfWeek;
      });
    }
  });
}

function renderCalendar() {
  const year = calendarState.currentDate.getFullYear();
  const month = calendarState.currentDate.getMonth();
  
  // Update month/year display
  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];
  document.getElementById('calendar-month-year').textContent = `${monthNames[month]} ${year}`;
  
  // Get first day of month and number of days
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const daysInMonth = lastDay.getDate();
  const startingDayOfWeek = firstDay.getDay();
  
  // Get previous month's last days
  const prevMonth = new Date(year, month, 0);
  const daysInPrevMonth = prevMonth.getDate();
  
  const calendarDays = document.getElementById('calendar-days');
  calendarDays.innerHTML = '';
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  // Add previous month's days
  for (let i = startingDayOfWeek - 1; i >= 0; i--) {
    const day = daysInPrevMonth - i;
    const dayEl = createCalendarDay(day, true, new Date(year, month - 1, day));
    calendarDays.appendChild(dayEl);
  }
  
  // Add current month's days
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month, day);
    date.setHours(0, 0, 0, 0);
    const isToday = date.getTime() === today.getTime();
    const dayEl = createCalendarDay(day, false, date, isToday);
    calendarDays.appendChild(dayEl);
  }
  
  // Add next month's days to fill the grid
  const totalCells = calendarDays.children.length;
  const remainingCells = 42 - totalCells; // 6 rows x 7 days
  for (let day = 1; day <= remainingCells; day++) {
    const dayEl = createCalendarDay(day, true, new Date(year, month + 1, day));
    calendarDays.appendChild(dayEl);
  }
}

function createCalendarDay(day, otherMonth, date, isToday = false) {
  const dayEl = document.createElement('div');
  dayEl.className = `calendar-day ${otherMonth ? 'other-month' : ''} ${isToday ? 'today' : ''}`;
  dayEl.dataset.date = date.toISOString().split('T')[0];
  
  const dayNumber = document.createElement('div');
  dayNumber.className = 'calendar-day-number';
  dayNumber.textContent = day;
  dayEl.appendChild(dayNumber);
  
  const sessionsContainer = document.createElement('div');
  sessionsContainer.className = 'sessions-container';
  sessionsContainer.id = `sessions-${date.toISOString().split('T')[0]}`;
  dayEl.appendChild(sessionsContainer);
  
  // Click handler to create session on that day
  dayEl.addEventListener('click', (e) => {
    if (!e.target.classList.contains('calendar-session')) {
      calendarState.selectedDate = date;
      openSessionModal(date);
    }
  });
  
  return dayEl;
}

async function loadSessions() {
  try {
    const year = calendarState.currentDate.getFullYear();
    const month = calendarState.currentDate.getMonth();
    
    // Get first and last day of month
    const startDate = new Date(year, month, 1);
    const endDate = new Date(year, month + 1, 0, 23, 59, 59);
    
    const params = {
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString()
    };
    
    if (calendarState.filterTrainer) params.trainer_id = calendarState.filterTrainer;
    if (calendarState.filterClient) params.client_id = calendarState.filterClient;
    if (calendarState.filterStatus) params.status = calendarState.filterStatus;
    
    const response = await sessionAPI.getAll(params);
    state.sessions = response.data;
    
    // Clear all session displays
    document.querySelectorAll('.sessions-container').forEach(c => c.innerHTML = '');
    
    // Display sessions on calendar
    state.sessions.forEach(session => {
      const sessionDate = new Date(session.session_date);
      const dateStr = sessionDate.toISOString().split('T')[0];
      const container = document.getElementById(`sessions-${dateStr}`);
      
      if (container) {
        const sessionEl = document.createElement('div');
        sessionEl.className = `calendar-session ${session.status}`;
        sessionEl.textContent = `${sessionDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })} ${session.client_name || 'Client'}`;
        sessionEl.title = `${session.trainer_name} - ${session.client_name}`;
        sessionEl.addEventListener('click', (e) => {
          e.stopPropagation();
          openSessionModal(null, session);
        });
        container.appendChild(sessionEl);
      }
    });
    
    // Update upcoming sessions list
    renderUpcomingSessions();
  } catch (error) {
    console.error('Error loading sessions:', error);
    showToast('Error loading sessions');
  }
}

function renderUpcomingSessions() {
  const container = document.getElementById('upcoming-sessions-list');
  const now = new Date();
  
  const upcomingSessions = state.sessions
    .filter(s => new Date(s.session_date) >= now && s.status === 'scheduled')
    .sort((a, b) => new Date(a.session_date) - new Date(b.session_date))
    .slice(0, 10);
  
  if (upcomingSessions.length === 0) {
    container.innerHTML = '<p class="text-gray-400">No upcoming sessions</p>';
    return;
  }
  
  container.innerHTML = upcomingSessions.map(session => {
    const sessionDate = new Date(session.session_date);
    return `
      <div class="session-list-item ${session.status} rounded-lg cursor-pointer hover:shadow-md transition-shadow" onclick="window.editSession(${session.id})">
        <div class="flex justify-between items-start">
          <div>
            <p class="font-semibold text-neutral-900">${session.client_name} - ${session.trainer_name}</p>
            <p class="text-sm text-gray-600">${sessionDate.toLocaleDateString()} at ${sessionDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</p>
            <p class="text-xs text-gray-500">${session.duration} min • ${session.session_type || 'Training'}</p>
          </div>
          <span class="text-xs px-2 py-1 rounded ${session.status === 'scheduled' ? 'bg-blue-100 text-blue-800' : ''}">
            ${session.status}
          </span>
        </div>
      </div>
    `;
  }).join('');
}

function openSessionModal(date = null, session = null) {
  const modal = document.getElementById('session-modal');
  const form = document.getElementById('session-form');
  const title = document.getElementById('session-modal-title');
  
  // Populate trainer and client dropdowns
  const trainers = Array.isArray(state.trainers) ? state.trainers : (state.trainers.items || []);
  const clients = Array.isArray(state.clients) ? state.clients : (state.clients.items || []);
  
  document.getElementById('session-trainer').innerHTML = '<option value="">Select trainer...</option>' +
    trainers.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
  
  document.getElementById('session-client').innerHTML = '<option value="">Select client...</option>' +
    clients.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  
  if (session) {
    // Edit mode - hide recurring options for existing sessions
    title.textContent = 'Edit Session';
    document.getElementById('session-id').value = session.id;
    document.getElementById('session-recurring').closest('.border-t').style.display = 'none';
    
    const sessionDate = new Date(session.session_date);
    document.getElementById('session-trainer').value = session.trainer_id;
    document.getElementById('session-client').value = session.client_id;
    document.getElementById('session-date').value = sessionDate.toISOString().split('T')[0];
    document.getElementById('session-time').value = sessionDate.toTimeString().slice(0, 5);
    document.getElementById('session-duration').value = session.duration;
    document.getElementById('session-type').value = session.session_type || 'personal';
    document.getElementById('session-location').value = session.location || '';
    document.getElementById('session-status').value = session.status;
    document.getElementById('session-notes').value = session.notes || '';
  } else {
    // Create mode - show recurring options
    title.textContent = 'New Session';
    form.reset();
    document.getElementById('session-id').value = '';
    document.getElementById('session-recurring').closest('.border-t').style.display = 'block';
    document.getElementById('recurring-options').classList.add('hidden');
    
    if (date) {
      document.getElementById('session-date').value = date.toISOString().split('T')[0];
      document.getElementById('session-time').value = '09:00';
    }
  }
  
  modal.classList.remove('hidden');
}

function closeSessionModal() {
  document.getElementById('session-modal').classList.add('hidden');
  document.getElementById('session-form').reset();
}

async function handleSessionSubmit(e) {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const sessionId = document.getElementById('session-id').value;
  const isRecurring = document.getElementById('session-recurring').checked;
  
  // Combine date and time
  const date = formData.get('date');
  const time = formData.get('time');
  const sessionDate = new Date(`${date}T${time}`);
  
  const baseData = {
    trainer_id: parseInt(formData.get('trainer_id')),
    client_id: parseInt(formData.get('client_id')),
    duration: parseInt(formData.get('duration')),
    session_type: formData.get('session_type'),
    location: formData.get('location'),
    notes: formData.get('notes')
  };
  
  try {
    if (sessionId) {
      // Update existing session
      const data = {
        ...baseData,
        session_date: sessionDate.toISOString(),
        status: formData.get('status')
      };
      await sessionAPI.update(sessionId, data);
      showToast('Session updated successfully');
    } else if (isRecurring) {
      // Create recurring session
      const recurrenceDays = Array.from(
        document.querySelectorAll('input[name="recurrence_days"]:checked')
      ).map(cb => parseInt(cb.value));
      
      const recurringData = {
        ...baseData,
        start_time: time,
        start_date: date,
        end_date: formData.get('recurrence_end_date') || null,
        recurrence_pattern: formData.get('recurrence_pattern'),
        recurrence_days: recurrenceDays.length > 0 ? recurrenceDays : null
      };
      
      const response = await recurringSessionAPI.create(recurringData);
      showToast(`Recurring session created! ${response.data.sessions_created} sessions scheduled.`);
    } else {
      // Create single session
      const data = {
        ...baseData,
        session_date: sessionDate.toISOString(),
        status: formData.get('status')
      };
      await sessionAPI.create(data);
      showToast('Session created successfully');
    }
    
    closeSessionModal();
    loadSessions();
  } catch (error) {
    console.error('Error saving session:', error);
    if (error.response && error.response.status === 409) {
      showToast('Session conflicts with existing booking');
    } else {
      showToast('Error saving session: ' + (error.response?.data?.error || error.message));
    }
  }
}

// Make editSession available globally
window.editSession = async function(id) {
  try {
    const response = await sessionAPI.getById(id);
    openSessionModal(null, response.data);
  } catch (error) {
    console.error('Error loading session:', error);
    showToast('Error loading session');
  }
};

// ===== Progress Tracking Functions =====
function loadProgressSection() {
  // Load clients into dropdown
  const clientSelect = document.getElementById('progress-client-select');
  clientSelect.innerHTML = '<option value="">Choose a client...</option>';
  
  state.clients.forEach(client => {
    const option = document.createElement('option');
    option.value = client.id;
    option.textContent = `${client.first_name} ${client.last_name}`;
    clientSelect.appendChild(option);
  });
}

// Progress client selection handler
document.getElementById('progress-client-select').addEventListener('change', async (e) => {
  const clientId = e.target.value;
  const addBtn = document.getElementById('add-measurement-btn');
  const emptyState = document.getElementById('progress-empty-state');
  const chartsContainer = document.getElementById('progress-charts');
  
  if (!clientId) {
    addBtn.disabled = true;
    emptyState.classList.remove('hidden');
    chartsContainer.classList.add('hidden');
    state.selectedProgressClient = null;
    return;
  }
  
  state.selectedProgressClient = clientId;
  addBtn.disabled = false;
  emptyState.classList.add('hidden');
  chartsContainer.classList.remove('hidden');
  
  await loadClientProgress(clientId);
});

async function loadClientProgress(clientId) {
  try {
    // Get progress data
    const response = await measurementAPI.getProgress(clientId);
    const progressData = response.data;
    
    // Update charts
    updateWeightChart(progressData.weight);
    updateBodyCompositionChart(progressData.body_composition);
    updateCircumferencesChart(progressData.circumferences);
    updateVitalsChart(progressData.vitals);
    
    // Update measurements table
    const measurementsResponse = await measurementAPI.getAll({ client_id: clientId, per_page: 10 });
    updateMeasurementsTable(measurementsResponse.data.measurements);
    
    // Load progress photos
    const photosResponse = await progressPhotoAPI.getAll({ client_id: clientId });
    state.progressPhotos = photosResponse.data.data || [];
    renderProgressPhotos(state.progressPhotos);
    
    // Load comparison view
    const comparisonResponse = await progressPhotoAPI.getComparison(clientId);
    renderComparisonView(comparisonResponse.data.data);
    
    // Load goals
    const goalsResponse = await goalAPI.getSummary(clientId);
    state.goals = goalsResponse.data.data.goals || [];
    renderGoals(state.goals);
    
  } catch (error) {
    console.error('Error loading progress:', error);
    showToast('Error loading progress data');
  }
}

function updateWeightChart(weightData) {
  const ctx = document.getElementById('weight-chart');
  
  // Destroy existing chart
  if (state.charts.weight) {
    state.charts.weight.destroy();
  }
  
  state.charts.weight = new Chart(ctx, {
    type: 'line',
    data: {
      labels: weightData.dates,
      datasets: [{
        label: 'Weight',
        data: weightData.values,
        borderColor: '#f97316',
        backgroundColor: 'rgba(249, 115, 22, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          labels: { color: '#fff' }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(156, 163, 175, 0.1)' }
        },
        x: {
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(156, 163, 175, 0.1)' }
        }
      }
    }
  });
}

function updateBodyCompositionChart(bodyCompData) {
  const ctx = document.getElementById('body-composition-chart');
  
  if (state.charts.bodyComposition) {
    state.charts.bodyComposition.destroy();
  }
  
  state.charts.bodyComposition = new Chart(ctx, {
    type: 'line',
    data: {
      labels: bodyCompData.dates,
      datasets: [
        {
          label: 'Body Fat %',
          data: bodyCompData.body_fat,
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          label: 'Muscle Mass',
          data: bodyCompData.muscle_mass,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          yAxisID: 'y1'
        },
        {
          label: 'BMI',
          data: bodyCompData.bmi,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          yAxisID: 'y2'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          labels: { color: '#fff' }
        }
      },
      scales: {
        y: {
          type: 'linear',
          position: 'left',
          title: { display: true, text: 'Body Fat %', color: '#9ca3af' },
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(156, 163, 175, 0.1)' }
        },
        y1: {
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'Muscle Mass', color: '#9ca3af' },
          ticks: { color: '#9ca3af' },
          grid: { drawOnChartArea: false }
        },
        y2: {
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'BMI', color: '#9ca3af' },
          ticks: { color: '#9ca3af' },
          grid: { drawOnChartArea: false }
        },
        x: {
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(156, 163, 175, 0.1)' }
        }
      }
    }
  });
}

function updateCircumferencesChart(circumferencesData) {
  const ctx = document.getElementById('circumferences-chart');
  
  if (state.charts.circumferences) {
    state.charts.circumferences.destroy();
  }
  
  const datasets = [];
  const colors = ['#f97316', '#ef4444', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];
  let colorIndex = 0;
  
  Object.keys(circumferencesData).forEach(key => {
    if (key !== 'dates' && circumferencesData[key].some(v => v !== null)) {
      datasets.push({
        label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        data: circumferencesData[key],
        borderColor: colors[colorIndex % colors.length],
        backgroundColor: `${colors[colorIndex % colors.length]}20`,
        tension: 0.4
      });
      colorIndex++;
    }
  });
  
  state.charts.circumferences = new Chart(ctx, {
    type: 'line',
    data: {
      labels: circumferencesData.dates,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          labels: { color: '#fff' }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(156, 163, 175, 0.1)' }
        },
        x: {
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(156, 163, 175, 0.1)' }
        }
      }
    }
  });
}

function updateVitalsChart(vitalsData) {
  const ctx = document.getElementById('vitals-chart');
  
  if (state.charts.vitals) {
    state.charts.vitals.destroy();
  }
  
  state.charts.vitals = new Chart(ctx, {
    type: 'line',
    data: {
      labels: vitalsData.dates,
      datasets: [
        {
          label: 'Resting Heart Rate',
          data: vitalsData.resting_heart_rate,
          borderColor: '#f97316',
          backgroundColor: 'rgba(249, 115, 22, 0.1)',
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          label: 'Systolic BP',
          data: vitalsData.blood_pressure_systolic,
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
          yAxisID: 'y1'
        },
        {
          label: 'Diastolic BP',
          data: vitalsData.blood_pressure_diastolic,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          labels: { color: '#fff' }
        }
      },
      scales: {
        y: {
          type: 'linear',
          position: 'left',
          title: { display: true, text: 'Heart Rate (bpm)', color: '#9ca3af' },
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(156, 163, 175, 0.1)' }
        },
        y1: {
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'Blood Pressure (mmHg)', color: '#9ca3af' },
          ticks: { color: '#9ca3af' },
          grid: { drawOnChartArea: false }
        },
        x: {
          ticks: { color: '#9ca3af' },
          grid: { color: 'rgba(156, 163, 175, 0.1)' }
        }
      }
    }
  });
}

function updateMeasurementsTable(measurements) {
  const tbody = document.getElementById('measurements-table-body');
  
  if (!measurements || measurements.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center text-gray-400">No measurements recorded</td></tr>';
    return;
  }
  
  tbody.innerHTML = measurements.map(m => `
    <tr>
      <td>${new Date(m.recorded_at).toLocaleDateString()}</td>
      <td>${m.weight ? `${m.weight} ${m.weight_unit}` : '-'}</td>
      <td>${m.body_fat_percentage ? `${m.body_fat_percentage}%` : '-'}</td>
      <td>${m.muscle_mass ? `${m.muscle_mass}` : '-'}</td>
      <td>${m.bmi ? m.bmi.toFixed(1) : '-'}</td>
      <td>${m.resting_heart_rate ? `${m.resting_heart_rate} bpm` : '-'}</td>
      <td>${m.blood_pressure_systolic && m.blood_pressure_diastolic ? 
        `${m.blood_pressure_systolic}/${m.blood_pressure_diastolic}` : '-'}</td>
      <td>
        <button onclick="editMeasurement(${m.id})" class="text-primary-500 hover:text-primary-400 mr-2">Edit</button>
        <button onclick="deleteMeasurement(${m.id})" class="text-red-500 hover:text-red-400">Delete</button>
      </td>
    </tr>
  `).join('');
}

// Measurement modal handlers
document.getElementById('add-measurement-btn').addEventListener('click', () => {
  openMeasurementModal();
});

document.getElementById('close-measurement-modal').addEventListener('click', () => {
  closeMeasurementModal();
});

document.getElementById('cancel-measurement-btn').addEventListener('click', () => {
  closeMeasurementModal();
});

function openMeasurementModal(measurement = null) {
  const modal = document.getElementById('measurement-modal');
  const form = document.getElementById('measurement-form');
  const title = document.getElementById('measurement-modal-title');
  
  form.reset();
  
  if (measurement) {
    title.textContent = 'Edit Measurement';
    document.getElementById('measurement-id').value = measurement.id;
    document.getElementById('measurement-client-id').value = measurement.client_id;
    
    // Fill in all fields
    if (measurement.weight) document.getElementById('measurement-weight').value = measurement.weight;
    if (measurement.weight_unit) document.getElementById('measurement-weight-unit').value = measurement.weight_unit;
    if (measurement.body_fat_percentage) document.getElementById('measurement-body-fat').value = measurement.body_fat_percentage;
    if (measurement.muscle_mass) document.getElementById('measurement-muscle-mass').value = measurement.muscle_mass;
    if (measurement.bmi) document.getElementById('measurement-bmi').value = measurement.bmi;
    if (measurement.chest) document.getElementById('measurement-chest').value = measurement.chest;
    if (measurement.waist) document.getElementById('measurement-waist').value = measurement.waist;
    if (measurement.hips) document.getElementById('measurement-hips').value = measurement.hips;
    if (measurement.thigh_left) document.getElementById('measurement-thigh-left').value = measurement.thigh_left;
    if (measurement.thigh_right) document.getElementById('measurement-thigh-right').value = measurement.thigh_right;
    if (measurement.arm_left) document.getElementById('measurement-arm-left').value = measurement.arm_left;
    if (measurement.arm_right) document.getElementById('measurement-arm-right').value = measurement.arm_right;
    if (measurement.calf_left) document.getElementById('measurement-calf-left').value = measurement.calf_left;
    if (measurement.calf_right) document.getElementById('measurement-calf-right').value = measurement.calf_right;
    if (measurement.measurement_unit) document.getElementById('measurement-unit').value = measurement.measurement_unit;
    if (measurement.resting_heart_rate) document.getElementById('measurement-resting-hr').value = measurement.resting_heart_rate;
    if (measurement.blood_pressure_systolic) document.getElementById('measurement-bp-systolic').value = measurement.blood_pressure_systolic;
    if (measurement.blood_pressure_diastolic) document.getElementById('measurement-bp-diastolic').value = measurement.blood_pressure_diastolic;
    if (measurement.notes) document.getElementById('measurement-notes').value = measurement.notes;
  } else {
    title.textContent = 'New Measurement';
    document.getElementById('measurement-client-id').value = state.selectedProgressClient;
  }
  
  modal.classList.remove('hidden');
}

function closeMeasurementModal() {
  document.getElementById('measurement-modal').classList.add('hidden');
  document.getElementById('measurement-form').reset();
}

// Measurement form submission
document.getElementById('measurement-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const data = {
    client_id: parseInt(formData.get('client_id'))
  };
  
  // Add all measurement fields (only if they have values)
  const fields = [
    'weight', 'weight_unit', 'body_fat_percentage', 'muscle_mass', 'bmi',
    'chest', 'waist', 'hips', 'thigh_left', 'thigh_right', 
    'arm_left', 'arm_right', 'calf_left', 'calf_right', 'measurement_unit',
    'resting_heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic', 'notes'
  ];
  
  fields.forEach(field => {
    const value = formData.get(field);
    if (value && value !== '') {
      // Convert numeric fields
      if (['weight', 'body_fat_percentage', 'muscle_mass', 'bmi', 
           'chest', 'waist', 'hips', 'thigh_left', 'thigh_right',
           'arm_left', 'arm_right', 'calf_left', 'calf_right',
           'resting_heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic'].includes(field)) {
        data[field] = parseFloat(value);
      } else {
        data[field] = value;
      }
    }
  });
  
  try {
    const measurementId = formData.get('id');
    
    if (measurementId) {
      await measurementAPI.update(measurementId, data);
      showToast('Measurement updated successfully');
    } else {
      await measurementAPI.create(data);
      showToast('Measurement added successfully');
    }
    
    closeMeasurementModal();
    await loadClientProgress(data.client_id);
  } catch (error) {
    console.error('Error saving measurement:', error);
    showToast('Error saving measurement: ' + (error.response?.data?.error || error.message));
  }
});

// Make measurement functions globally available
window.editMeasurement = async function(id) {
  try {
    const response = await measurementAPI.getById(id);
    openMeasurementModal(response.data);
  } catch (error) {
    console.error('Error loading measurement:', error);
    showToast('Error loading measurement');
  }
};

window.deleteMeasurement = async function(id) {
  if (!confirm('Are you sure you want to delete this measurement?')) return;
  
  try {
    await measurementAPI.delete(id);
    showToast('Measurement deleted successfully');
    await loadClientProgress(state.selectedProgressClient);
  } catch (error) {
    console.error('Error deleting measurement:', error);
    showToast('Error deleting measurement');
  }
};

// ===== File Management Functions =====
async function loadFilesSection() {
  // Load clients into file filter dropdown
  const clientSelect = document.getElementById('files-client-select');
  const fileClientSelect = document.getElementById('file-client');
  
  clientSelect.innerHTML = '<option value="">All Files</option>';
  fileClientSelect.innerHTML = '<option value="">No client</option>';
  
  state.clients.forEach(client => {
    const option1 = document.createElement('option');
    option1.value = client.id;
    option1.textContent = `${client.first_name} ${client.last_name}`;
    clientSelect.appendChild(option1);
    
    const option2 = document.createElement('option');
    option2.value = client.id;
    option2.textContent = `${client.first_name} ${client.last_name}`;
    fileClientSelect.appendChild(option2);
  });
  
  // Load categories
  try {
    const categoriesResponse = await fileAPI.getCategories();
    const categoryFilter = document.getElementById('files-category-filter');
    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    
    categoriesResponse.data.categories.forEach(cat => {
      const option = document.createElement('option');
      option.value = cat.value;
      option.textContent = cat.label;
      categoryFilter.appendChild(option);
    });
  } catch (error) {
    console.error('Error loading categories:', error);
  }
  
  await loadFiles();
  await loadFileStats();
}

async function loadFiles() {
  try {
    const params = {
      page: state.filesPagination.page,
      per_page: state.filesPagination.per_page
    };
    
    // Add filters
    const clientFilter = document.getElementById('files-client-select').value;
    const categoryFilter = document.getElementById('files-category-filter').value;
    
    if (clientFilter) params.client_id = clientFilter;
    if (categoryFilter) params.category = categoryFilter;
    
    const response = await fileAPI.getAll(params);
    state.files = response.data.files;
    state.filesPagination.total = response.data.total;
    state.filesPagination.pages = response.data.pages;
    
    renderFilesTable();
    updateFilesPagination();
  } catch (error) {
    console.error('Error loading files:', error);
    showToast('Error loading files');
  }
}

async function loadFileStats() {
  try {
    const clientFilter = document.getElementById('files-client-select').value;
    const params = clientFilter ? { client_id: clientFilter } : {};
    
    const response = await fileAPI.getStats(params);
    const stats = response.data;
    
    document.getElementById('total-files-count').textContent = stats.total_files;
    document.getElementById('total-storage-used').textContent = stats.total_size_mb + ' MB';
    document.getElementById('total-categories').textContent = Object.keys(stats.by_category).length;
  } catch (error) {
    console.error('Error loading file stats:', error);
  }
}

function renderFilesTable() {
  const tbody = document.getElementById('files-table-body');
  
  if (!state.files || state.files.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-center text-gray-400">No files found</td></tr>';
    return;
  }
  
  tbody.innerHTML = state.files.map(file => {
    const clientName = file.client_id && state.clients.find(c => c.id === file.client_id)
      ? `${state.clients.find(c => c.id === file.client_id).first_name} ${state.clients.find(c => c.id === file.client_id).last_name}`
      : '-';
    
    const fileSize = file.file_size ? (file.file_size / 1024).toFixed(2) + ' KB' : '-';
    const uploadDate = new Date(file.created_at).toLocaleDateString();
    
    return `
      <tr>
        <td>
          <div class="flex items-center gap-2">
            ${getFileIcon(file.file_type)}
            <span class="font-medium">${file.original_filename}</span>
          </div>
        </td>
        <td>
          <span class="px-2 py-1 text-xs rounded-full bg-primary-100 text-primary-800">
            ${formatCategory(file.category)}
          </span>
        </td>
        <td>${clientName}</td>
        <td>${fileSize}</td>
        <td>${uploadDate}</td>
        <td>
          <div class="flex gap-2">
            <button onclick="downloadFile(${file.id}, '${file.original_filename}')" class="text-primary-500 hover:text-primary-400" title="Download">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
              </svg>
            </button>
            <button onclick="deleteFile(${file.id})" class="text-red-500 hover:text-red-400" title="Delete">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function getFileIcon(fileType) {
  if (!fileType) return '<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>';
  
  if (fileType.startsWith('image/')) {
    return '<svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>';
  } else if (fileType === 'application/pdf') {
    return '<svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>';
  } else if (fileType.startsWith('video/')) {
    return '<svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>';
  }
  
  return '<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>';
}

function formatCategory(category) {
  const categoryMap = {
    'workout_plan': 'Workout Plan',
    'waiver': 'Waiver',
    'assessment': 'Assessment',
    'progress_photo': 'Progress Photo',
    'document': 'Document',
    'video': 'Video',
    'other': 'Other'
  };
  return categoryMap[category] || category;
}

function updateFilesPagination() {
  const start = (state.filesPagination.page - 1) * state.filesPagination.per_page + 1;
  const end = Math.min(state.filesPagination.page * state.filesPagination.per_page, state.filesPagination.total);
  
  document.getElementById('files-showing-start').textContent = state.filesPagination.total > 0 ? start : 0;
  document.getElementById('files-showing-end').textContent = end;
  document.getElementById('files-total').textContent = state.filesPagination.total;
  
  document.getElementById('files-prev-page').disabled = state.filesPagination.page === 1;
  document.getElementById('files-next-page').disabled = state.filesPagination.page >= state.filesPagination.pages;
}

// File filter handlers
document.getElementById('files-client-select').addEventListener('change', () => {
  state.filesPagination.page = 1;
  loadFiles();
  loadFileStats();
});

document.getElementById('files-category-filter').addEventListener('change', () => {
  state.filesPagination.page = 1;
  loadFiles();
});

// File pagination handlers
document.getElementById('files-prev-page').addEventListener('click', () => {
  if (state.filesPagination.page > 1) {
    state.filesPagination.page--;
    loadFiles();
  }
});

document.getElementById('files-next-page').addEventListener('click', () => {
  if (state.filesPagination.page < state.filesPagination.pages) {
    state.filesPagination.page++;
    loadFiles();
  }
});

// File upload modal handlers
document.getElementById('upload-file-btn').addEventListener('click', () => {
  openFileUploadModal();
});

document.getElementById('close-file-modal').addEventListener('click', () => {
  closeFileUploadModal();
});

document.getElementById('cancel-file-btn').addEventListener('click', () => {
  closeFileUploadModal();
});

function openFileUploadModal() {
  document.getElementById('file-upload-modal').classList.remove('hidden');
  document.getElementById('file-upload-form').reset();
  document.getElementById('selected-file-name').classList.add('hidden');
}

function closeFileUploadModal() {
  document.getElementById('file-upload-modal').classList.add('hidden');
  document.getElementById('file-upload-form').reset();
  document.getElementById('selected-file-name').classList.add('hidden');
}

// File input and drag-drop
const fileInput = document.getElementById('file-input');
const fileDropZone = document.getElementById('file-drop-zone');
const selectedFileName = document.getElementById('selected-file-name');

fileDropZone.addEventListener('click', () => {
  fileInput.click();
});

fileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    const file = e.target.files[0];
    selectedFileName.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
    selectedFileName.classList.remove('hidden');
  }
});

// Drag and drop
fileDropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  fileDropZone.classList.add('border-primary-500', 'bg-primary-50');
});

fileDropZone.addEventListener('dragleave', () => {
  fileDropZone.classList.remove('border-primary-500', 'bg-primary-50');
});

fileDropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  fileDropZone.classList.remove('border-primary-500', 'bg-primary-50');
  
  if (e.dataTransfer.files.length > 0) {
    fileInput.files = e.dataTransfer.files;
    const file = e.dataTransfer.files[0];
    selectedFileName.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
    selectedFileName.classList.remove('hidden');
  }
});

// File upload form submission
document.getElementById('file-upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  
  // Add uploaded_by (hardcoded for now - should come from auth)
  formData.append('uploaded_by', '1');
  
  const submitBtn = document.getElementById('upload-file-submit-btn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Uploading...';
  
  try {
    await fileAPI.upload(formData);
    showToast('File uploaded successfully');
    closeFileUploadModal();
    await loadFiles();
    await loadFileStats();
  } catch (error) {
    console.error('Error uploading file:', error);
    showToast('Error uploading file: ' + (error.response?.data?.error || error.message));
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `
      <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
      </svg>
      Upload File
    `;
  }
});

// Make file functions globally available
window.downloadFile = function(id, filename) {
  fileAPI.download(id, filename);
};

window.deleteFile = async function(id) {
  if (!confirm('Are you sure you want to delete this file?')) return;
  
  try {
    await fileAPI.delete(id);
    showToast('File deleted successfully');
    await loadFiles();
    await loadFileStats();
  } catch (error) {
    console.error('Error deleting file:', error);
    showToast('Error deleting file');
  }
};

// ===== Workout Management Functions =====
async function loadWorkoutsSection() {
  // Load initial data
  await loadExerciseFilters();
  await loadWorkoutCategories();
  await loadExercises();
  
  // Load clients for assignments
  const assignmentSelect = document.getElementById('assignment-client-select');
  assignmentSelect.innerHTML = '<option value="">Choose a client...</option>';
  state.clients.forEach(client => {
    const option = document.createElement('option');
    option.value = client.id;
    option.textContent = `${client.first_name} ${client.last_name}`;
    assignmentSelect.appendChild(option);
  });
  
  // Seed exercises if needed
  if (state.exercises.length === 0) {
    try {
      await exerciseAPI.seed();
      await loadExercises();
      showToast('Exercise library initialized with 20 common exercises');
    } catch (error) {
      console.error('Error seeding exercises:', error);
    }
  }
}

// Tab Management
document.getElementById('tab-exercises').addEventListener('click', () => {
  switchWorkoutTab('exercises');
});

document.getElementById('tab-templates').addEventListener('click', () => {
  switchWorkoutTab('templates');
  loadWorkoutTemplates();
});

document.getElementById('tab-assignments').addEventListener('click', () => {
  switchWorkoutTab('assignments');
});

function switchWorkoutTab(tab) {
  state.currentWorkoutTab = tab;
  
  // Update tab buttons
  document.querySelectorAll('.workout-tab').forEach(btn => btn.classList.remove('active'));
  document.getElementById(`tab-${tab}`).classList.add('active');
  
  // Update tab content
  document.querySelectorAll('.workout-tab-content').forEach(content => content.classList.add('hidden'));
  document.getElementById(`${tab}-tab-content`).classList.remove('hidden');
}

// Exercise Library Functions
async function loadExerciseFilters() {
  try {
    const [categoriesRes, muscleRes, equipmentRes] = await Promise.all([
      exerciseAPI.getCategories(),
      exerciseAPI.getMuscleGroups(),
      exerciseAPI.getEquipment()
    ]);
    
    // Populate category filters
    const categoryFilter = document.getElementById('exercise-category-filter');
    const exerciseCategory = document.getElementById('exercise-category');
    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    exerciseCategory.innerHTML = '<option value="">Select...</option>';
    
    categoriesRes.data.categories.forEach(cat => {
      const opt1 = document.createElement('option');
      opt1.value = cat.value;
      opt1.textContent = cat.label;
      categoryFilter.appendChild(opt1);
      
      const opt2 = opt1.cloneNode(true);
      exerciseCategory.appendChild(opt2);
    });
    
    // Populate muscle group filter
    const muscleFilter = document.getElementById('exercise-muscle-filter');
    const exerciseMuscle = document.getElementById('exercise-muscle');
    muscleFilter.innerHTML = '<option value="">All Muscle Groups</option>';
    exerciseMuscle.innerHTML = '<option value="">Select...</option>';
    
    muscleRes.data.muscle_groups.forEach(muscle => {
      const opt1 = document.createElement('option');
      opt1.value = muscle.value;
      opt1.textContent = muscle.label;
      muscleFilter.appendChild(opt1);
      
      const opt2 = opt1.cloneNode(true);
      exerciseMuscle.appendChild(opt2);
    });
    
    // Populate equipment dropdown
    const exerciseEquipment = document.getElementById('exercise-equipment');
    exerciseEquipment.innerHTML = '<option value="">Select...</option>';
    
    equipmentRes.data.equipment.forEach(eq => {
      const opt = document.createElement('option');
      opt.value = eq.value;
      opt.textContent = eq.label;
      exerciseEquipment.appendChild(opt);
    });
    
  } catch (error) {
    console.error('Error loading exercise filters:', error);
  }
}

async function loadExercises() {
  try {
    const params = {};
    
    const search = document.getElementById('exercise-search').value;
    const category = document.getElementById('exercise-category-filter').value;
    const muscle = document.getElementById('exercise-muscle-filter').value;
    
    if (search) params.search = search;
    if (category) params.category = category;
    if (muscle) params.muscle_group = muscle;
    
    const response = await exerciseAPI.getAll(params);
    state.exercises = response.data.exercises;
    
    renderExercises();
  } catch (error) {
    console.error('Error loading exercises:', error);
    showToast('Error loading exercises');
  }
}

function renderExercises() {
  const grid = document.getElementById('exercises-grid');
  
  if (!state.exercises || state.exercises.length === 0) {
    grid.innerHTML = '<div class="text-center py-12 col-span-full"><p class="text-gray-400">No exercises found</p></div>';
    return;
  }
  
  grid.innerHTML = state.exercises.map(exercise => `
    <div class="exercise-card">
      <h3>${exercise.name}</h3>
      <div class="mb-3">
        ${exercise.category ? `<span class="badge bg-blue-100 text-blue-800">${formatCategory(exercise.category)}</span>` : ''}
        ${exercise.muscle_group ? `<span class="badge bg-green-100 text-green-800">${formatMuscleGroup(exercise.muscle_group)}</span>` : ''}
        ${exercise.difficulty ? `<span class="badge bg-orange-100 text-orange-800">${capitalize(exercise.difficulty)}</span>` : ''}
      </div>
      ${exercise.description ? `<p class="text-sm text-gray-600 mb-3">${exercise.description}</p>` : ''}
      <div class="flex gap-2 justify-end">
        <button onclick="viewExercise(${exercise.id})" class="text-primary-500 hover:text-primary-600 text-sm font-medium">View</button>
        ${exercise.is_custom ? `<button onclick="editExercise(${exercise.id})" class="text-blue-500 hover:text-blue-600 text-sm font-medium">Edit</button>` : ''}
        ${exercise.is_custom ? `<button onclick="deleteExercise(${exercise.id})" class="text-red-500 hover:text-red-600 text-sm font-medium">Delete</button>` : ''}
      </div>
    </div>
  `).join('');
}

// Helper functions for formatting
function formatMuscleGroup(muscle) {
  const map = {
    'chest': 'Chest',
    'back': 'Back',
    'legs': 'Legs',
    'shoulders': 'Shoulders',
    'arms': 'Arms',
    'core': 'Core',
    'full_body': 'Full Body'
  };
  return map[muscle] || muscle;
}

// Exercise filters
document.getElementById('exercise-search').addEventListener('input', debounce(loadExercises, 300));
document.getElementById('exercise-category-filter').addEventListener('change', loadExercises);
document.getElementById('exercise-muscle-filter').addEventListener('change', loadExercises);

function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// Exercise modal handlers
document.getElementById('add-exercise-btn').addEventListener('click', () => {
  openExerciseModal();
});

document.getElementById('close-exercise-modal').addEventListener('click', () => {
  closeExerciseModal();
});

document.getElementById('cancel-exercise-btn').addEventListener('click', () => {
  closeExerciseModal();
});

function openExerciseModal(exercise = null) {
  const modal = document.getElementById('exercise-modal');
  const form = document.getElementById('exercise-form');
  const title = document.getElementById('exercise-modal-title');
  
  form.reset();
  
  if (exercise) {
    title.textContent = 'Edit Exercise';
    document.getElementById('exercise-id').value = exercise.id;
    document.getElementById('exercise-name').value = exercise.name;
    if (exercise.category) document.getElementById('exercise-category').value = exercise.category;
    if (exercise.muscle_group) document.getElementById('exercise-muscle').value = exercise.muscle_group;
    if (exercise.equipment) document.getElementById('exercise-equipment').value = exercise.equipment;
    if (exercise.difficulty) document.getElementById('exercise-difficulty').value = exercise.difficulty;
    if (exercise.description) document.getElementById('exercise-description').value = exercise.description;
    if (exercise.instructions) document.getElementById('exercise-instructions').value = exercise.instructions;
    if (exercise.tips) document.getElementById('exercise-tips').value = exercise.tips;
    if (exercise.image_url) document.getElementById('exercise-image').value = exercise.image_url;
    if (exercise.video_url) document.getElementById('exercise-video').value = exercise.video_url;
  } else {
    title.textContent = 'Add Exercise';
  }
  
  modal.classList.remove('hidden');
}

function closeExerciseModal() {
  document.getElementById('exercise-modal').classList.add('hidden');
}

// Exercise form submission
document.getElementById('exercise-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const data = {
    name: formData.get('name'),
    category: formData.get('category') || null,
    muscle_group: formData.get('muscle_group') || null,
    equipment: formData.get('equipment') || null,
    difficulty: formData.get('difficulty') || null,
    description: formData.get('description') || null,
    instructions: formData.get('instructions') || null,
    tips: formData.get('tips') || null,
    image_url: formData.get('image_url') || null,
    video_url: formData.get('video_url') || null,
    is_custom: true,
    created_by: 1 // TODO: Get from auth
  };
  
  try {
    const exerciseId = formData.get('id');
    
    if (exerciseId) {
      await exerciseAPI.update(exerciseId, data);
      showToast('Exercise updated successfully');
    } else {
      await exerciseAPI.create(data);
      showToast('Exercise added successfully');
    }
    
    closeExerciseModal();
    await loadExercises();
  } catch (error) {
    console.error('Error saving exercise:', error);
    showToast('Error saving exercise: ' + (error.response?.data?.error || error.message));
  }
});

// Workout Template Functions
async function loadWorkoutCategories() {
  try {
    const response = await workoutAPI.getCategories();
    const templateCategory = document.getElementById('template-category');
    const templateFilter = document.getElementById('template-category-filter');
    
    templateCategory.innerHTML = '<option value="">Select...</option>';
    templateFilter.innerHTML = '<option value="">All Categories</option>';
    
    response.data.categories.forEach(cat => {
      const opt1 = document.createElement('option');
      opt1.value = cat.value;
      opt1.textContent = cat.label;
      templateCategory.appendChild(opt1);
      
      const opt2 = opt1.cloneNode(true);
      templateFilter.appendChild(opt2);
    });
  } catch (error) {
    console.error('Error loading workout categories:', error);
  }
}

async function loadWorkoutTemplates() {
  try {
    const params = { user_id: 1 }; // TODO: Get from auth
    
    const search = document.getElementById('template-search').value;
    const category = document.getElementById('template-category-filter').value;
    
    if (search) params.search = search;
    if (category) params.category = category;
    
    const response = await workoutAPI.getAllTemplates(params);
    state.workoutTemplates = response.data.templates;
    
    renderWorkoutTemplates();
  } catch (error) {
    console.error('Error loading workout templates:', error);
    showToast('Error loading templates');
  }
}

function renderWorkoutTemplates() {
  const grid = document.getElementById('templates-grid');
  
  if (!state.workoutTemplates || state.workoutTemplates.length === 0) {
    grid.innerHTML = '<div class="text-center py-12 col-span-full"><p class="text-gray-400">No templates yet. Create your first workout template!</p></div>';
    return;
  }
  
  grid.innerHTML = state.workoutTemplates.map(template => `
    <div class="card">
      <h3 class="text-xl font-semibold text-neutral-900 mb-2">${template.name}</h3>
      ${template.description ? `<p class="text-sm text-gray-600 mb-3">${template.description}</p>` : ''}
      <div class="mb-3">
        ${template.category ? `<span class="badge bg-blue-100 text-blue-800">${formatCategory(template.category)}</span>` : ''}
        ${template.difficulty ? `<span class="badge bg-orange-100 text-orange-800">${capitalize(template.difficulty)}</span>` : ''}
        ${template.duration_minutes ? `<span class="badge bg-green-100 text-green-800">${template.duration_minutes} min</span>` : ''}
        ${template.is_public ? `<span class="badge bg-purple-100 text-purple-800">Public</span>` : ''}
      </div>
      <div class="flex gap-2 justify-end">
        <button onclick="viewTemplate(${template.id})" class="text-primary-500 hover:text-primary-600 text-sm font-medium">View</button>
        <button onclick="editTemplate(${template.id})" class="text-blue-500 hover:text-blue-600 text-sm font-medium">Edit</button>
        <button onclick="deleteTemplate(${template.id})" class="text-red-500 hover:text-red-600 text-sm font-medium">Delete</button>
      </div>
    </div>
  `).join('');
}

// View Template Function
window.viewTemplate = async function(templateId) {
  try {
    const response = await workoutAPI.getTemplateById(templateId);
    openWorkoutViewModal(response);
  } catch (error) {
    showToast('Error loading workout template');
    console.error(error);
  }
};

window.editTemplate = function(templateId) {
  // Open the workout view modal in edit mode
  viewTemplate(templateId);
};

window.deleteTemplate = async function(templateId) {
  if (!confirm('Are you sure you want to delete this workout template?')) return;
  
  try {
    await workoutAPI.deleteTemplate(templateId);
    showToast('Template deleted successfully');
    loadWorkoutTemplates();
  } catch (error) {
    showToast('Error deleting template');
    console.error(error);
  }
};

// Workout View Modal Functions
function openWorkoutViewModal(template) {
  const modal = document.getElementById('workout-view-modal');
  const form = document.getElementById('workout-view-form');
  
  // Populate form
  document.getElementById('workout-view-id').value = template.id;
  document.getElementById('workout-view-name').value = template.name || '';
  document.getElementById('workout-view-description').value = template.description || '';
  document.getElementById('workout-view-category').value = template.category || '';
  document.getElementById('workout-view-difficulty').value = template.difficulty || '';
  document.getElementById('workout-view-duration').value = template.duration_minutes || '';
  document.getElementById('workout-view-image').value = template.image_url || '';
  document.getElementById('workout-view-video').value = template.video_url || '';
  document.getElementById('workout-view-public').checked = template.is_public || false;
  
  // Load category options
  loadWorkoutCategoriesForView();
  
  // Render media preview
  renderMediaPreview(template);
  
  // Render exercises
  renderWorkoutViewExercises(template.exercises || []);
  
  // Set view mode (read-only)
  setWorkoutViewMode(false);
  
  modal.classList.remove('hidden');
}

function closeWorkoutViewModal() {
  document.getElementById('workout-view-modal').classList.add('hidden');
}

function setWorkoutViewMode(isEditing) {
  const fields = ['workout-view-name', 'workout-view-description', 'workout-view-duration', 'workout-view-image', 'workout-view-video'];
  const selects = ['workout-view-category', 'workout-view-difficulty'];
  const checkbox = document.getElementById('workout-view-public');
  const toggleBtn = document.getElementById('workout-edit-toggle-btn');
  const toggleText = document.getElementById('workout-edit-toggle-text');
  const actions = document.getElementById('workout-view-actions');
  
  fields.forEach(id => {
    const field = document.getElementById(id);
    if (isEditing) {
      field.removeAttribute('readonly');
      field.classList.remove('bg-gray-50');
    } else {
      field.setAttribute('readonly', 'readonly');
      field.classList.add('bg-gray-50');
    }
  });
  
  selects.forEach(id => {
    const select = document.getElementById(id);
    if (isEditing) {
      select.removeAttribute('disabled');
      select.classList.remove('bg-gray-50');
    } else {
      select.setAttribute('disabled', 'disabled');
      select.classList.add('bg-gray-50');
    }
  });
  
  if (isEditing) {
    checkbox.removeAttribute('disabled');
    toggleText.textContent = 'Cancel Edit';
    actions.classList.remove('hidden');
  } else {
    checkbox.setAttribute('disabled', 'disabled');
    toggleText.textContent = 'Edit';
    actions.classList.add('hidden');
  }
}

function renderMediaPreview(template) {
  const mediaPreview = document.getElementById('workout-media-preview');
  const imageContainer = document.getElementById('workout-image-container');
  const videoContainer = document.getElementById('workout-video-container');
  const imagePreview = document.getElementById('workout-image-preview');
  const videoLink = document.getElementById('workout-video-link');
  
  let hasMedia = false;
  
  if (template.image_url) {
    imagePreview.src = template.image_url;
    imageContainer.classList.remove('hidden');
    hasMedia = true;
  } else {
    imageContainer.classList.add('hidden');
  }
  
  if (template.video_url) {
    videoLink.href = template.video_url;
    videoContainer.classList.remove('hidden');
    hasMedia = true;
  } else {
    videoContainer.classList.add('hidden');
  }
  
  if (hasMedia) {
    mediaPreview.classList.remove('hidden');
  } else {
    mediaPreview.classList.add('hidden');
  }
}

function renderWorkoutViewExercises(exercises) {
  const container = document.getElementById('workout-view-exercises');
  
  if (!exercises || exercises.length === 0) {
    container.innerHTML = '<div class="text-center py-8 border-2 border-dashed border-neutral-300 rounded-lg"><p class="text-gray-500">No exercises in this workout yet.</p></div>';
    return;
  }
  
  container.innerHTML = exercises.map((item, idx) => `
    <div class="border border-neutral-200 rounded-lg p-4">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-sm font-semibold text-gray-500">#${idx + 1}</span>
            <h4 class="font-semibold text-neutral-900">${item.exercise?.name || 'Exercise'}</h4>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
            <div><span class="text-gray-600">Sets:</span> <span class="font-medium">${item.sets || '-'}</span></div>
            <div><span class="text-gray-600">Reps:</span> <span class="font-medium">${item.reps || '-'}</span></div>
            <div><span class="text-gray-600">Rest:</span> <span class="font-medium">${item.rest_seconds || 0}s</span></div>
            <div><span class="text-gray-600">Weight:</span> <span class="font-medium">${item.weight || '-'}</span></div>
            ${item.notes ? `<div class="col-span-full"><span class="text-gray-600">Notes:</span> <span class="font-medium">${item.notes}</span></div>` : ''}
          </div>
        </div>
      </div>
    </div>
  `).join('');
}

async function loadWorkoutCategoriesForView() {
  try {
    const response = await workoutAPI.getCategories();
    const select = document.getElementById('workout-view-category');
    select.innerHTML = '<option value="">Select...</option>' + 
      response.categories.map(cat => `<option value="${cat.value}">${cat.label}</option>`).join('');
  } catch (error) {
    console.error('Error loading categories:', error);
  }
}

// Event Listeners for Workout View Modal
document.getElementById('close-workout-view-modal').addEventListener('click', closeWorkoutViewModal);

document.getElementById('workout-edit-toggle-btn').addEventListener('click', () => {
  const toggleText = document.getElementById('workout-edit-toggle-text');
  const isCurrentlyEditing = toggleText.textContent === 'Cancel Edit';
  
  if (isCurrentlyEditing) {
    // Cancel editing - reload the template
    const templateId = document.getElementById('workout-view-id').value;
    if (templateId) {
      viewTemplate(parseInt(templateId));
    }
  } else {
    // Enable editing
    setWorkoutViewMode(true);
  }
});

document.getElementById('workout-view-cancel-btn').addEventListener('click', () => {
  const templateId = document.getElementById('workout-view-id').value;
  if (templateId) {
    viewTemplate(parseInt(templateId));
  }
});

document.getElementById('workout-view-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const templateId = document.getElementById('workout-view-id').value;
  const formData = new FormData(e.target);
  
  const data = {
    name: formData.get('name'),
    description: formData.get('description') || null,
    category: formData.get('category') || null,
    difficulty: formData.get('difficulty') || null,
    duration_minutes: formData.get('duration_minutes') ? parseInt(formData.get('duration_minutes')) : null,
    image_url: formData.get('image_url') || null,
    video_url: formData.get('video_url') || null,
    is_public: formData.get('is_public') === 'on'
  };
  
  try {
    await workoutAPI.updateTemplate(templateId, data);
    showToast('Workout updated successfully');
    loadWorkoutTemplates();
    viewTemplate(parseInt(templateId)); // Reload the view
  } catch (error) {
    showToast('Error updating workout');
    console.error(error);
  }
});

document.getElementById('workout-assign-btn').addEventListener('click', () => {
  const templateId = document.getElementById('workout-view-id').value;
  if (templateId) {
    openAssignWorkoutModal(parseInt(templateId));
  }
});

async function openAssignWorkoutModal(templateId) {
  const modal = document.getElementById('assign-workout-modal');
  const clientSelect = document.getElementById('assign-client-select');
  const templateSelect = document.getElementById('assign-template-select');
  
  // Populate clients
  if (state.clients.length === 0) {
    const response = await clientAPI.getAll();
    state.clients = response.clients || [];
  }
  
  clientSelect.innerHTML = '<option value="">Select client...</option>';
  state.clients.forEach(client => {
    const option = document.createElement('option');
    option.value = client.id;
    option.textContent = `${client.first_name} ${client.last_name}`;
    if (state.selectedAssignmentClient && client.id === parseInt(state.selectedAssignmentClient)) {
      option.selected = true;
    }
    clientSelect.appendChild(option);
  });
  
  // Populate templates
  if (state.workoutTemplates.length === 0) {
    await loadWorkoutTemplates();
  }
  
  templateSelect.innerHTML = '<option value="">Select template...</option>';
  state.workoutTemplates.forEach(template => {
    const option = document.createElement('option');
    option.value = template.id;
    option.textContent = template.name;
    // Pre-select the template if provided
    if (templateId && template.id === templateId) {
      option.selected = true;
    }
    templateSelect.appendChild(option);
  });
  
  modal.classList.remove('hidden');
}

// Template filters
document.getElementById('template-search').addEventListener('input', debounce(loadWorkoutTemplates, 300));
document.getElementById('template-category-filter').addEventListener('change', loadWorkoutTemplates);

// Template modal handlers
document.getElementById('create-template-btn').addEventListener('click', () => {
  openTemplateModal();
});

document.getElementById('close-template-modal').addEventListener('click', () => {
  closeTemplateModal();
});

document.getElementById('cancel-template-btn').addEventListener('click', () => {
  closeTemplateModal();
});

function openTemplateModal(template = null) {
  const modal = document.getElementById('template-modal');
  const form = document.getElementById('template-form');
  const title = document.getElementById('template-modal-title');
  
  form.reset();
  state.templateExercises = [];
  
  if (template) {
    title.textContent = 'Edit Workout Template';
    // TODO: Load template data
  } else {
    title.textContent = 'Create Workout Template';
  }
  
  renderTemplateExercises();
  modal.classList.remove('hidden');
}

function closeTemplateModal() {
  document.getElementById('template-modal').classList.add('hidden');
  state.templateExercises = [];
}

// Template form submission
document.getElementById('template-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const data = {
    name: formData.get('name'),
    description: formData.get('description') || null,
    category: formData.get('category') || null,
    difficulty: formData.get('difficulty') || null,
    duration_minutes: formData.get('duration_minutes') ? parseInt(formData.get('duration_minutes')) : null,
    is_public: formData.get('is_public') === 'on',
    created_by: 1, // TODO: Get from auth
    exercises: state.templateExercises
  };
  
  try {
    await workoutAPI.createTemplate(data);
    showToast('Workout template created successfully');
    closeTemplateModal();
    await loadWorkoutTemplates();
    switchWorkoutTab('templates');
  } catch (error) {
    console.error('Error creating template:', error);
    showToast('Error creating template: ' + (error.response?.data?.error || error.message));
  }
});

// Add exercise to template
document.getElementById('add-exercise-to-template-btn').addEventListener('click', () => {
  openExerciseSelectorModal();
});

function openExerciseSelectorModal() {
  const modal = document.getElementById('exercise-selector-modal');
  renderExerciseSelector();
  modal.classList.remove('hidden');
}

document.getElementById('close-exercise-selector-modal').addEventListener('click', () => {
  document.getElementById('exercise-selector-modal').classList.add('hidden');
});

function renderExerciseSelector() {
  const list = document.getElementById('exercise-selector-list');
  
  if (!state.exercises || state.exercises.length === 0) {
    list.innerHTML = '<div class="text-center py-12"><p class="text-gray-400">No exercises available</p></div>';
    return;
  }
  
  list.innerHTML = state.exercises.map(exercise => `
    <div class="flex items-center justify-between p-3 border border-neutral-200 rounded-lg hover:bg-neutral-50 cursor-pointer" onclick="selectExerciseForTemplate(${exercise.id})">
      <div>
        <h4 class="font-semibold text-neutral-900">${exercise.name}</h4>
        <p class="text-sm text-gray-600">
          ${exercise.muscle_group ? formatMuscleGroup(exercise.muscle_group) : ''} 
          ${exercise.equipment ? `• ${exercise.equipment}` : ''}
        </p>
      </div>
      <button class="btn-primary py-2 px-4">Add</button>
    </div>
  `).join('');
}

window.selectExerciseForTemplate = function(exerciseId) {
  const exercise = state.exercises.find(ex => ex.id === exerciseId);
  if (!exercise) return;
  
  state.templateExercises.push({
    exercise_id: exercise.id,
    exercise: exercise,
    order: state.templateExercises.length,
    sets: 3,
    reps: '10',
    rest_seconds: 60,
    weight: '',
    notes: ''
  });
  
  document.getElementById('exercise-selector-modal').classList.add('hidden');
  renderTemplateExercises();
};

function renderTemplateExercises() {
  const list = document.getElementById('template-exercises-list');
  
  if (state.templateExercises.length === 0) {
    list.innerHTML = '<div class="text-center py-8 border-2 border-dashed border-neutral-300 rounded-lg"><p class="text-gray-500">No exercises added yet. Click "Add Exercise" to get started.</p></div>';
    return;
  }
  
  list.innerHTML = state.templateExercises.map((item, idx) => `
    <div class="template-exercise-item">
      <div class="flex-1">
        <h4 class="font-semibold text-neutral-900 mb-2">${item.exercise.name}</h4>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-2">
          <input type="number" value="${item.sets}" onchange="updateTemplateExercise(${idx}, 'sets', this.value)" class="input-field py-1" placeholder="Sets" min="1">
          <input type="text" value="${item.reps}" onchange="updateTemplateExercise(${idx}, 'reps', this.value)" class="input-field py-1" placeholder="Reps">
          <input type="number" value="${item.rest_seconds}" onchange="updateTemplateExercise(${idx}, 'rest_seconds', this.value)" class="input-field py-1" placeholder="Rest (s)" min="0">
          <input type="text" value="${item.weight}" onchange="updateTemplateExercise(${idx}, 'weight', this.value)" class="input-field py-1" placeholder="Weight">
          <input type="text" value="${item.notes}" onchange="updateTemplateExercise(${idx}, 'notes', this.value)" class="input-field py-1" placeholder="Notes">
        </div>
      </div>
      <button onclick="removeTemplateExercise(${idx})" class="text-red-500 hover:text-red-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>
  `).join('');
}

window.updateTemplateExercise = function(idx, field, value) {
  if (state.templateExercises[idx]) {
    state.templateExercises[idx][field] = field === 'sets' || field === 'rest_seconds' ? parseInt(value) || 0 : value;
  }
};

window.removeTemplateExercise = function(idx) {
  state.templateExercises.splice(idx, 1);
  renderTemplateExercises();
};

// Client Assignment Functions
document.getElementById('assignment-client-select').addEventListener('change', async (e) => {
  const clientId = e.target.value;
  const assignBtn = document.getElementById('assign-workout-btn');
  
  if (!clientId) {
    assignBtn.disabled = true;
    document.getElementById('assignments-list').innerHTML = '<div class="text-center py-12"><p class="text-gray-400">Select a client to view their workout assignments</p></div>';
    return;
  }
  
  state.selectedAssignmentClient = clientId;
  assignBtn.disabled = false;
  
  await loadClientAssignments(clientId);
});

async function loadClientAssignments(clientId) {
  try {
    const response = await workoutAPI.getClientAssignments(clientId);
    state.clientAssignments = response.data.assignments;
    
    renderClientAssignments();
  } catch (error) {
    console.error('Error loading assignments:', error);
    showToast('Error loading assignments');
  }
}

function renderClientAssignments() {
  const list = document.getElementById('assignments-list');
  
  if (!state.clientAssignments || state.clientAssignments.length === 0) {
    list.innerHTML = '<div class="text-center py-12"><p class="text-gray-400">No workout assignments for this client</p></div>';
    return;
  }
  
  list.innerHTML = state.clientAssignments.map(assignment => `
    <div class="card">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h3 class="text-xl font-semibold text-neutral-900 mb-2">${assignment.workout_template?.name || 'Workout'}</h3>
          ${assignment.workout_template?.description ? `<p class="text-sm text-gray-600 mb-3">${assignment.workout_template.description}</p>` : ''}
          <div class="text-sm text-gray-600">
            ${assignment.start_date ? `<p>Start: ${new Date(assignment.start_date).toLocaleDateString()}</p>` : ''}
            ${assignment.end_date ? `<p>End: ${new Date(assignment.end_date).toLocaleDateString()}</p>` : ''}
            ${assignment.frequency_per_week ? `<p>Frequency: ${assignment.frequency_per_week}x per week</p>` : ''}
          </div>
        </div>
        <span class="px-3 py-1 text-sm rounded-full ${getStatusClass(assignment.status)}">${capitalize(assignment.status)}</span>
      </div>
    </div>
  `).join('');
}

function getStatusClass(status) {
  const classes = {
    'active': 'bg-green-100 text-green-800',
    'completed': 'bg-blue-100 text-blue-800',
    'paused': 'bg-gray-100 text-gray-800'
  };
  return classes[status] || 'bg-gray-100 text-gray-800';
}

// Assign workout modal
document.getElementById('assign-workout-btn').addEventListener('click', () => {
  openAssignWorkoutModal();
});

document.getElementById('close-assign-modal').addEventListener('click', () => {
  closeAssignWorkoutModal();
});

document.getElementById('cancel-assign-btn').addEventListener('click', () => {
  closeAssignWorkoutModal();
});

function closeAssignWorkoutModal() {
  document.getElementById('assign-workout-modal').classList.add('hidden');
  document.getElementById('assign-workout-form').reset();
}

document.getElementById('assign-workout-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const data = {
    client_id: parseInt(formData.get('client_id')),
    workout_template_id: parseInt(formData.get('workout_template_id')),
    assigned_by: 1, // TODO: Get from auth
    start_date: formData.get('start_date') || null,
    end_date: formData.get('end_date') || null,
    frequency_per_week: formData.get('frequency_per_week') ? parseInt(formData.get('frequency_per_week')) : null,
    notes: formData.get('notes') || null
  };
  
  try {
    await workoutAPI.assignWorkout(data);
    showToast('Workout assigned successfully');
    closeAssignWorkoutModal();
    if (state.selectedAssignmentClient) {
      await loadClientAssignments(state.selectedAssignmentClient);
    }
  } catch (error) {
    console.error('Error assigning workout:', error);
    showToast('Error assigning workout: ' + (error.response?.data?.error || error.message));
  }
});

// Global exercise functions
window.viewExercise = async function(id) {
  try {
    const response = await exerciseAPI.getById(id);
    const exercise = response.data;
    alert(`${exercise.name}\n\n${exercise.description || ''}\n\n${exercise.instructions || ''}`);
  } catch (error) {
    console.error('Error viewing exercise:', error);
    showToast('Error loading exercise details');
  }
};

window.editExercise = async function(id) {
  try {
    const response = await exerciseAPI.getById(id);
    openExerciseModal(response.data);
  } catch (error) {
    console.error('Error loading exercise:', error);
    showToast('Error loading exercise');
  }
};

window.deleteExercise = async function(id) {
  if (!confirm('Are you sure you want to delete this exercise?')) return;
  
  try {
    await exerciseAPI.delete(id);
    showToast('Exercise deleted successfully');
    await loadExercises();
  } catch (error) {
    console.error('Error deleting exercise:', error);
    showToast('Error: ' + (error.response?.data?.error || error.message));
  }
};

window.viewTemplate = async function(id) {
  try {
    const response = await workoutAPI.getTemplate(id);
    const template = response.data;
    let details = `${template.name}\n\n${template.description || ''}\n\nExercises:\n`;
    template.exercises.forEach((ex, idx) => {
      details += `\n${idx + 1}. ${ex.exercise.name} - ${ex.sets} sets x ${ex.reps} reps`;
    });
    alert(details);
  } catch (error) {
    console.error('Error viewing template:', error);
    showToast('Error loading template details');
  }
};

window.editTemplate = async function(id) {
  showToast('Edit template feature coming soon!');
  // TODO: Implement edit template
};

window.deleteTemplate = async function(id) {
  if (!confirm('Are you sure you want to delete this workout template?')) return;
  
  try {
    await workoutAPI.deleteTemplate(id);
    showToast('Template deleted successfully');
    await loadWorkoutTemplates();
  } catch (error) {
    console.error('Error deleting template:', error);
    showToast('Error: ' + (error.response?.data?.error || error.message));
  }
};

// ===== Progress Photo Functions =====
function renderProgressPhotos(photos) {
  const grid = document.getElementById('progress-photos-grid');
  
  if (!photos || photos.length === 0) {
    grid.innerHTML = '<div class="text-center text-gray-400 col-span-full py-8">No photos uploaded</div>';
    return;
  }
  
  grid.innerHTML = photos.map(photo => `
    <div class="photo-item">
      <img src="${progressPhotoAPI.getFile(photo.id)}" alt="${photo.caption || 'Progress photo'}" />
      <div class="photo-overlay">
        <div class="flex gap-2">
          <button onclick="deleteProgressPhoto(${photo.id})" class="bg-red-500 text-white p-2 rounded">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="p-2 bg-neutral-800">
        <p class="text-sm text-white">${photo.photo_type} - ${new Date(photo.taken_date).toLocaleDateString()}</p>
        ${photo.caption ? `<p class="text-xs text-gray-400">${photo.caption}</p>` : ''}
      </div>
    </div>
  `).join('');
}

function renderComparisonView(comparisonData) {
  const photoTypes = ['front', 'side', 'back'];
  
  photoTypes.forEach(type => {
    const container = document.getElementById(`comparison-${type}`);
    const data = comparisonData[type];
    
    if (!data || !data.before) {
      container.innerHTML = '<div class="text-gray-400">No photos available</div>';
      return;
    }
    
    container.innerHTML = `
      <div class="comparison-images">
        <div class="comparison-image">
          <img src="${progressPhotoAPI.getFile(data.before.id)}" alt="Before" />
          <span class="comparison-label">Before</span>
          <p class="text-xs text-gray-400 mt-1">${new Date(data.before.taken_date).toLocaleDateString()}</p>
        </div>
        ${data.after ? `
          <div class="comparison-image">
            <img src="${progressPhotoAPI.getFile(data.after.id)}" alt="After" />
            <span class="comparison-label">After</span>
            <p class="text-xs text-gray-400 mt-1">${new Date(data.after.taken_date).toLocaleDateString()}</p>
          </div>
        ` : '<div class="text-gray-400 flex items-center justify-center">Keep taking photos to see progress!</div>'}
      </div>
    `;
  });
}

function renderGoals(goals) {
  const container = document.getElementById('goals-list');
  
  if (!goals || goals.length === 0) {
    container.innerHTML = '<div class="text-center text-gray-400 py-8">No goals set</div>';
    return;
  }
  
  container.innerHTML = goals.map(goal => `
    <div class="goal-card priority-${goal.priority} status-${goal.status}">
      <div class="flex justify-between items-start">
        <div class="flex-1">
          <h4 class="font-semibold text-lg text-neutral-900">${goal.title}</h4>
          <p class="text-sm text-gray-600 mt-1">${goal.description || ''}</p>
        </div>
        <div class="flex gap-2">
          <button onclick="editGoal(${goal.id})" class="text-blue-600 hover:text-blue-700">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
          </button>
          <button onclick="deleteGoal(${goal.id})" class="text-red-600 hover:text-red-700">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="mt-3">
        <div class="flex justify-between text-sm text-gray-600 mb-1">
          <span>Progress: ${goal.progress}%</span>
          ${goal.target_value ? `<span>${goal.current_value || 0} / ${goal.target_value} ${goal.target_unit || ''}</span>` : ''}
        </div>
        <div class="progress-bar">
          <div class="progress-bar-fill" style="width: ${goal.progress}%"></div>
        </div>
      </div>
      <div class="mt-2 flex flex-wrap gap-2 text-xs">
        <span class="px-2 py-1 bg-neutral-200 rounded-full">${goal.category}</span>
        <span class="px-2 py-1 bg-neutral-200 rounded-full">${goal.priority} priority</span>
        <span class="px-2 py-1 ${goal.status === 'completed' ? 'bg-green-200' : 'bg-blue-200'} rounded-full">${goal.status}</span>
        ${goal.target_date ? `<span class="px-2 py-1 bg-neutral-200 rounded-full">Target: ${new Date(goal.target_date).toLocaleDateString()}</span>` : ''}
      </div>
      ${goal.milestones && goal.milestones.length > 0 ? `
        <div class="mt-3 pt-3 border-t border-gray-200">
          <p class="text-sm font-medium text-gray-700 mb-2">Milestones:</p>
          <ul class="space-y-1">
            ${goal.milestones.map(m => `
              <li class="flex items-center text-sm ${m.completed ? 'text-green-600 line-through' : 'text-gray-600'}">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${m.completed ? 'M5 13l4 4L19 7' : 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'}"/>
                </svg>
                ${m.title}
              </li>
            `).join('')}
          </ul>
        </div>
      ` : ''}
    </div>
  `).join('');
}

// Progress Photo Modal Handlers
document.getElementById('upload-progress-photo-btn')?.addEventListener('click', () => {
  if (!state.selectedProgressClient) {
    showToast('Please select a client first');
    return;
  }
  document.getElementById('progress-photo-modal').classList.remove('hidden');
  document.getElementById('progress-photo-date').valueAsDate = new Date();
});

document.getElementById('close-progress-photo-modal')?.addEventListener('click', () => {
  document.getElementById('progress-photo-modal').classList.add('hidden');
  document.getElementById('progress-photo-form').reset();
});

document.getElementById('cancel-progress-photo-btn')?.addEventListener('click', () => {
  document.getElementById('progress-photo-modal').classList.add('hidden');
  document.getElementById('progress-photo-form').reset();
});

document.getElementById('progress-photo-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  try {
    const formData = new FormData();
    const fileInput = document.getElementById('progress-photo-file');
    formData.append('file', fileInput.files[0]);
    formData.append('client_id', state.selectedProgressClient);
    formData.append('photo_type', document.getElementById('progress-photo-type').value);
    formData.append('taken_date', document.getElementById('progress-photo-date').value);
    formData.append('caption', document.getElementById('progress-photo-caption').value);
    
    await progressPhotoAPI.upload(formData);
    showToast('Progress photo uploaded successfully');
    document.getElementById('progress-photo-modal').classList.add('hidden');
    document.getElementById('progress-photo-form').reset();
    
    // Reload progress data
    await loadClientProgress(state.selectedProgressClient);
  } catch (error) {
    console.error('Error uploading photo:', error);
    showToast('Error: ' + (error.response?.data?.error || error.message));
  }
});

window.deleteProgressPhoto = async function(id) {
  if (!confirm('Are you sure you want to delete this photo?')) return;
  
  try {
    await progressPhotoAPI.delete(id);
    showToast('Photo deleted successfully');
    await loadClientProgress(state.selectedProgressClient);
  } catch (error) {
    console.error('Error deleting photo:', error);
    showToast('Error: ' + (error.response?.data?.error || error.message));
  }
};

// Goal Modal Handlers
document.getElementById('add-goal-btn')?.addEventListener('click', () => {
  if (!state.selectedProgressClient) {
    showToast('Please select a client first');
    return;
  }
  document.getElementById('goal-modal-title').textContent = 'Add Goal';
  document.getElementById('goal-id').value = '';
  document.getElementById('goal-form').reset();
  document.getElementById('goal-modal').classList.remove('hidden');
});

document.getElementById('close-goal-modal')?.addEventListener('click', () => {
  document.getElementById('goal-modal').classList.add('hidden');
  document.getElementById('goal-form').reset();
});

document.getElementById('cancel-goal-btn')?.addEventListener('click', () => {
  document.getElementById('goal-modal').classList.add('hidden');
  document.getElementById('goal-form').reset();
});

document.getElementById('goal-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const goalId = document.getElementById('goal-id').value;
  const goalData = {
    client_id: state.selectedProgressClient,
    title: document.getElementById('goal-title').value,
    description: document.getElementById('goal-description').value,
    category: document.getElementById('goal-category').value,
    target_value: parseFloat(document.getElementById('goal-target-value').value) || null,
    target_unit: document.getElementById('goal-target-unit').value,
    current_value: parseFloat(document.getElementById('goal-current-value').value) || 0,
    target_date: document.getElementById('goal-target-date').value || null,
    priority: document.getElementById('goal-priority').value,
    status: document.getElementById('goal-status').value,
    notes: document.getElementById('goal-notes').value,
  };
  
  try {
    if (goalId) {
      await goalAPI.update(goalId, goalData);
      showToast('Goal updated successfully');
    } else {
      await goalAPI.create(goalData);
      showToast('Goal created successfully');
    }
    
    document.getElementById('goal-modal').classList.add('hidden');
    document.getElementById('goal-form').reset();
    await loadClientProgress(state.selectedProgressClient);
  } catch (error) {
    console.error('Error saving goal:', error);
    showToast('Error: ' + (error.response?.data?.error || error.message));
  }
});

window.editGoal = async function(id) {
  try {
    const response = await goalAPI.getById(id);
    const goal = response.data.data;
    
    document.getElementById('goal-modal-title').textContent = 'Edit Goal';
    document.getElementById('goal-id').value = goal.id;
    document.getElementById('goal-title').value = goal.title;
    document.getElementById('goal-description').value = goal.description || '';
    document.getElementById('goal-category').value = goal.category;
    document.getElementById('goal-target-value').value = goal.target_value || '';
    document.getElementById('goal-target-unit').value = goal.target_unit || '';
    document.getElementById('goal-current-value').value = goal.current_value || '';
    document.getElementById('goal-target-date').value = goal.target_date ? goal.target_date.split('T')[0] : '';
    document.getElementById('goal-priority').value = goal.priority;
    document.getElementById('goal-status').value = goal.status;
    document.getElementById('goal-notes').value = goal.notes || '';
    
    document.getElementById('goal-modal').classList.remove('hidden');
  } catch (error) {
    console.error('Error loading goal:', error);
    showToast('Error loading goal');
  }
};

window.deleteGoal = async function(id) {
  if (!confirm('Are you sure you want to delete this goal?')) return;
  
  try {
    await goalAPI.delete(id);
    showToast('Goal deleted successfully');
    await loadClientProgress(state.selectedProgressClient);
  } catch (error) {
    console.error('Error deleting goal:', error);
    showToast('Error: ' + (error.response?.data?.error || error.message));
  }
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initCollapsibleSections();
  loadDashboard();
});
