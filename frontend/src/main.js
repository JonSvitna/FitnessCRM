import './styles/main.css';
import { trainerAPI, clientAPI, crmAPI, settingsAPI, activityAPI, sessionAPI } from './api.js';

// State management
let state = {
  trainers: [],
  clients: [],
  assignments: [],
  sessions: [],
  settings: null,
  trainersPagination: { page: 1, per_page: 25, total: 0, pages: 0 },
  clientsPagination: { page: 1, per_page: 25, total: 0, pages: 0 },
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
  
  // Modal controls
  document.getElementById('close-session-modal').addEventListener('click', closeSessionModal);
  document.getElementById('cancel-session-btn').addEventListener('click', closeSessionModal);
  
  // Session form
  document.getElementById('session-form').addEventListener('submit', handleSessionSubmit);
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
    // Edit mode
    title.textContent = 'Edit Session';
    document.getElementById('session-id').value = session.id;
    
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
    // Create mode
    title.textContent = 'New Session';
    form.reset();
    document.getElementById('session-id').value = '';
    
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
  
  // Combine date and time
  const date = formData.get('date');
  const time = formData.get('time');
  const sessionDate = new Date(`${date}T${time}`);
  
  const data = {
    trainer_id: parseInt(formData.get('trainer_id')),
    client_id: parseInt(formData.get('client_id')),
    session_date: sessionDate.toISOString(),
    duration: parseInt(formData.get('duration')),
    session_type: formData.get('session_type'),
    location: formData.get('location'),
    status: formData.get('status'),
    notes: formData.get('notes')
  };
  
  try {
    if (sessionId) {
      // Update existing session
      await sessionAPI.update(sessionId, data);
      showToast('Session updated successfully');
    } else {
      // Create new session
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
      showToast('Error saving session');
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

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  loadDashboard();
});
