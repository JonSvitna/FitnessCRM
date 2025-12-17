/**
 * SMS Management Interface
 * Phase 5: Communication - M5.2: SMS Integration Frontend
 */

import { smsAPI, clientAPI, trainerAPI } from './api.js';
import { showToast } from './main.js';
import { initCollapsibleSections } from './sidebar-sections.js';

// Global state
let currentTab = 'send';
let templates = [];
let schedules = [];
let logs = [];
let currentTemplateId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initializeSidebar();
  initCollapsibleSections();
  setupTabs();
  setupEventListeners();
  loadRecipients();
  loadTemplates();
  loadSchedules();
  loadLogs();
  loadAnalytics();
});

function initializeSidebar() {
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
  const mobileOverlay = document.getElementById('mobile-overlay');
  const sidebar = document.getElementById('sidebar');

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('sidebar-expanded');
      document.getElementById('main-content').classList.toggle('main-content-expanded');
    });
  }

  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('sidebar-mobile-open');
      mobileOverlay.classList.toggle('hidden');
    });
  }

  if (mobileOverlay) {
    mobileOverlay.addEventListener('click', () => {
      sidebar.classList.remove('sidebar-mobile-open');
      mobileOverlay.classList.add('hidden');
    });
  }
}

function setupTabs() {
  const tabs = ['send', 'templates', 'schedules', 'logs', 'analytics'];
  
  tabs.forEach(tab => {
    const tabBtn = document.getElementById(`tab-${tab}`);
    const content = document.getElementById(`content-${tab}`);
    
    if (tabBtn) {
      tabBtn.addEventListener('click', () => {
        // Update active tab
        document.querySelectorAll('.tab-button').forEach(btn => {
          btn.classList.remove('active', 'text-orange-600', 'border-b-2', 'border-orange-600');
          btn.classList.add('text-gray-500');
        });
        tabBtn.classList.add('active', 'text-orange-600', 'border-b-2', 'border-orange-600');
        tabBtn.classList.remove('text-gray-500');
        
        // Show content
        document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
        content.classList.remove('hidden');
        
        currentTab = tab;
      });
    }
  });
}

function setupEventListeners() {
  // Send SMS form
  const sendForm = document.getElementById('send-sms-form');
  if (sendForm) {
    sendForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await sendSMS();
    });
  }

  // Character count
  const messageInput = document.getElementById('sms-message');
  if (messageInput) {
    messageInput.addEventListener('input', () => {
      const count = messageInput.value.length;
      document.getElementById('sms-char-count').textContent = count;
    });
  }

  // Recipient select change
  const recipientSelect = document.getElementById('sms-recipient-select');
  if (recipientSelect) {
    recipientSelect.addEventListener('change', (e) => {
      const option = e.target.options[e.target.selectedIndex];
      if (option.dataset.phone) {
        document.getElementById('sms-phone').value = option.dataset.phone;
      }
    });
  }

  // Template form
  const templateForm = document.getElementById('template-form');
  if (templateForm) {
    templateForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await saveTemplate();
    });
  }

  // New template button
  const newTemplateBtn = document.getElementById('new-template-btn');
  if (newTemplateBtn) {
    newTemplateBtn.addEventListener('click', () => {
      openTemplateModal();
    });
  }

  // Cancel template
  const cancelTemplateBtn = document.getElementById('cancel-template-btn');
  if (cancelTemplateBtn) {
    cancelTemplateBtn.addEventListener('click', () => {
      closeTemplateModal();
    });
  }
}

async function loadRecipients() {
  try {
    const [clientsRes, trainersRes] = await Promise.all([
      clientAPI.getAll(),
      trainerAPI.getAll()
    ]);

    const select = document.getElementById('sms-recipient-select');
    if (!select) return;

    select.innerHTML = '<option value="">Select recipient...</option>';

    clientsRes.data.clients?.forEach(client => {
      if (client.phone) {
        const option = document.createElement('option');
        option.value = client.id;
        option.textContent = `${client.name} (Client)`;
        option.dataset.phone = client.phone;
        select.appendChild(option);
      }
    });

    trainersRes.data.trainers?.forEach(trainer => {
      if (trainer.phone) {
        const option = document.createElement('option');
        option.value = trainer.id;
        option.textContent = `${trainer.name} (Trainer)`;
        option.dataset.phone = trainer.phone;
        select.appendChild(option);
      }
    });
  } catch (error) {
    console.error('Error loading recipients:', error);
  }
}

async function sendSMS() {
  const phone = document.getElementById('sms-phone').value.trim();
  const message = document.getElementById('sms-message').value.trim();
  const recipientId = document.getElementById('sms-recipient-select').value;

  if (!phone || !message) {
    showToast('Please enter phone number and message', 'error');
    return;
  }

  try {
    const response = await smsAPI.send({
      to_number: phone,
      message: message,
      client_id: recipientId || null
    });

    if (response.data.success) {
      showToast('SMS sent successfully', 'success');
      document.getElementById('send-sms-form').reset();
      document.getElementById('sms-char-count').textContent = '0';
      loadLogs();
      loadAnalytics();
    } else {
      showToast(response.data.error || 'Failed to send SMS', 'error');
    }
  } catch (error) {
    console.error('Error sending SMS:', error);
    showToast('Failed to send SMS', 'error');
  }
}

async function loadTemplates() {
  try {
    const response = await smsAPI.getTemplates();
    templates = response.data.templates || [];
    renderTemplates();
  } catch (error) {
    console.error('Error loading templates:', error);
    showToast('Failed to load templates', 'error');
  }
}

function renderTemplates() {
  const container = document.getElementById('templates-list');
  if (!container) return;

  if (templates.length === 0) {
    container.innerHTML = '<div class="text-center text-gray-500 py-8">No templates yet. Create your first template!</div>';
    return;
  }

  container.innerHTML = templates.map(template => `
    <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h4 class="font-semibold text-gray-900">${escapeHtml(template.name)}</h4>
          <p class="text-sm text-gray-500 mt-1">${escapeHtml(template.category || 'custom')}</p>
          <p class="text-sm text-gray-700 mt-2">${escapeHtml(template.message)}</p>
        </div>
        <div class="flex items-center space-x-2 ml-4">
          <button onclick="useTemplate(${template.id})" class="text-orange-500 hover:text-orange-600 px-3 py-1 rounded text-sm font-medium">
            Use
          </button>
          <button onclick="editTemplate(${template.id})" class="text-gray-600 hover:text-gray-800 px-3 py-1 rounded text-sm font-medium">
            Edit
          </button>
          <button onclick="deleteTemplate(${template.id})" class="text-red-500 hover:text-red-600 px-3 py-1 rounded text-sm font-medium">
            Delete
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

async function loadSchedules() {
  try {
    const response = await smsAPI.getSchedules();
    schedules = response.data.schedules || [];
    renderSchedules();
  } catch (error) {
    console.error('Error loading schedules:', error);
  }
}

function renderSchedules() {
  const container = document.getElementById('schedules-list');
  if (!container) return;

  if (schedules.length === 0) {
    container.innerHTML = '<div class="text-center text-gray-500 py-8">No scheduled messages</div>';
    return;
  }

  container.innerHTML = schedules.map(schedule => `
    <div class="border border-gray-200 rounded-lg p-4">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h4 class="font-semibold text-gray-900">${escapeHtml(schedule.name || 'Scheduled SMS')}</h4>
          <p class="text-sm text-gray-500 mt-1">To: ${escapeHtml(schedule.to_number)}</p>
          <p class="text-sm text-gray-500">Scheduled: ${formatDateTime(schedule.scheduled_time)}</p>
          <p class="text-sm text-gray-500">Type: ${escapeHtml(schedule.schedule_type)}</p>
        </div>
        <div class="ml-4">
          <span class="px-3 py-1 rounded-full text-xs font-medium ${
            schedule.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
            schedule.status === 'sent' ? 'bg-green-100 text-green-800' :
            'bg-gray-100 text-gray-800'
          }">${escapeHtml(schedule.status)}</span>
          ${schedule.status === 'scheduled' ? `
            <button onclick="cancelSchedule(${schedule.id})" class="ml-2 text-red-500 hover:text-red-600 text-sm font-medium">
              Cancel
            </button>
          ` : ''}
        </div>
      </div>
    </div>
  `).join('');
}

async function loadLogs() {
  try {
    const response = await smsAPI.getLogs({ page: 1, per_page: 50 });
    logs = response.data.logs || [];
    renderLogs();
  } catch (error) {
    console.error('Error loading logs:', error);
  }
}

function renderLogs() {
  const container = document.getElementById('logs-list');
  if (!container) return;

  if (logs.length === 0) {
    container.innerHTML = '<div class="text-center text-gray-500 py-8">No SMS logs yet</div>';
    return;
  }

  container.innerHTML = logs.map(log => `
    <div class="border border-gray-200 rounded-lg p-4">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <p class="font-medium text-gray-900">${escapeHtml(log.to_number)}</p>
          <p class="text-sm text-gray-600 mt-1">${escapeHtml(log.message)}</p>
          <p class="text-xs text-gray-500 mt-2">${formatDateTime(log.created_at)}</p>
        </div>
        <div class="ml-4">
          <span class="px-3 py-1 rounded-full text-xs font-medium ${
            log.status === 'sent' || log.status === 'delivered' ? 'bg-green-100 text-green-800' :
            log.status === 'failed' ? 'bg-red-100 text-red-800' :
            'bg-gray-100 text-gray-800'
          }">${escapeHtml(log.status)}</span>
        </div>
      </div>
    </div>
  `).join('');
}

async function loadAnalytics() {
  try {
    const response = await smsAPI.getAnalytics();
    renderAnalytics(response.data);
  } catch (error) {
    console.error('Error loading analytics:', error);
  }
}

function renderAnalytics(data) {
  const container = document.getElementById('analytics-content');
  if (!container) return;

  container.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-gradient-to-br from-orange-400 to-orange-600 rounded-lg p-6 text-white">
        <h3 class="text-sm font-medium opacity-90">Total Sent</h3>
        <p class="text-3xl font-bold mt-2">${data.total_sent || 0}</p>
      </div>
      <div class="bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg p-6 text-white">
        <h3 class="text-sm font-medium opacity-90">Total Cost</h3>
        <p class="text-3xl font-bold mt-2">$${data.total_cost?.toFixed(2) || '0.00'}</p>
      </div>
      <div class="bg-gradient-to-br from-green-400 to-green-600 rounded-lg p-6 text-white">
        <h3 class="text-sm font-medium opacity-90">Status Breakdown</h3>
        <div class="mt-2 space-y-1">
          ${Object.entries(data.status_breakdown || {}).map(([status, count]) => `
            <p class="text-sm">${status}: ${count}</p>
          `).join('')}
        </div>
      </div>
    </div>
  `;
}

function openTemplateModal(templateId = null) {
  currentTemplateId = templateId;
  const modal = document.getElementById('template-modal');
  const form = document.getElementById('template-form');
  
  if (templateId) {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      document.getElementById('template-modal-title').textContent = 'Edit Template';
      document.getElementById('template-name').value = template.name;
      document.getElementById('template-category').value = template.category || 'custom';
      document.getElementById('template-message').value = template.message;
    }
  } else {
    document.getElementById('template-modal-title').textContent = 'New Template';
    form.reset();
  }
  
  modal.classList.remove('hidden');
}

function closeTemplateModal() {
  document.getElementById('template-modal').classList.add('hidden');
  currentTemplateId = null;
  document.getElementById('template-form').reset();
}

async function saveTemplate() {
  const name = document.getElementById('template-name').value.trim();
  const category = document.getElementById('template-category').value;
  const message = document.getElementById('template-message').value.trim();

  if (!name || !message) {
    showToast('Please fill in all required fields', 'error');
    return;
  }

  try {
    if (currentTemplateId) {
      await smsAPI.updateTemplate(currentTemplateId, { name, category, message });
      showToast('Template updated successfully', 'success');
    } else {
      await smsAPI.createTemplate({ name, category, message });
      showToast('Template created successfully', 'success');
    }
    
    closeTemplateModal();
    loadTemplates();
  } catch (error) {
    console.error('Error saving template:', error);
    showToast('Failed to save template', 'error');
  }
}

async function deleteTemplate(id) {
  if (!confirm('Are you sure you want to delete this template?')) return;

  try {
    await smsAPI.deleteTemplate(id);
    showToast('Template deleted successfully', 'success');
    loadTemplates();
  } catch (error) {
    console.error('Error deleting template:', error);
    showToast('Failed to delete template', 'error');
  }
}

async function cancelSchedule(id) {
  if (!confirm('Are you sure you want to cancel this scheduled SMS?')) return;

  try {
    await smsAPI.cancelSchedule(id);
    showToast('Schedule cancelled successfully', 'success');
    loadSchedules();
  } catch (error) {
    console.error('Error cancelling schedule:', error);
    showToast('Failed to cancel schedule', 'error');
  }
}

function useTemplate(id) {
  const template = templates.find(t => t.id === id);
  if (template) {
    document.getElementById('sms-message').value = template.message;
    document.getElementById('sms-char-count').textContent = template.message.length;
    // Switch to send tab
    document.getElementById('tab-send').click();
  }
}

function editTemplate(id) {
  openTemplateModal(id);
}

// Make functions available globally for onclick handlers
window.useTemplate = useTemplate;
window.editTemplate = editTemplate;
window.deleteTemplate = deleteTemplate;
window.cancelSchedule = cancelSchedule;

// Utility functions
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDateTime(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
}

