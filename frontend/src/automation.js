/**
 * Automation Rules Configuration Interface
 * Phase 5: Communication - M5.4: Automated Reminders Frontend
 */

import { automationAPI } from './api.js';
import { showToast } from './main.js';
import { initCollapsibleSections } from './sidebar-sections.js';

// Global state
let rules = [];
let logs = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initializeSidebar();
  initCollapsibleSections();
  setupTabs();
  setupEventListeners();
  loadRules();
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
  const tabs = ['rules', 'logs', 'analytics'];
  
  tabs.forEach(tab => {
    const tabBtn = document.getElementById(`tab-${tab}`);
    const content = document.getElementById(`content-${tab}`);
    
    if (tabBtn) {
      tabBtn.addEventListener('click', () => {
        document.querySelectorAll('.tab-button').forEach(btn => {
          btn.classList.remove('active', 'text-orange-600', 'border-b-2', 'border-orange-600');
          btn.classList.add('text-gray-500');
        });
        tabBtn.classList.add('active', 'text-orange-600', 'border-b-2', 'border-orange-600');
        tabBtn.classList.remove('text-gray-500');
        
        document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
        content.classList.remove('hidden');
      });
    }
  });
}

function setupEventListeners() {
  // New rule button
  const newRuleBtn = document.getElementById('new-rule-btn');
  if (newRuleBtn) {
    newRuleBtn.addEventListener('click', () => {
      openRuleModal();
    });
  }

  // Rule form
  const ruleForm = document.getElementById('rule-form');
  if (ruleForm) {
    ruleForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await saveRule();
    });
  }

  // Rule type change
  const ruleType = document.getElementById('rule-type');
  if (ruleType) {
    ruleType.addEventListener('change', (e) => {
      updateTriggerOptions(e.target.value);
    });
  }

  // Target change
  const targetSelect = document.getElementById('rule-target');
  if (targetSelect) {
    targetSelect.addEventListener('change', (e) => {
      const filters = document.getElementById('target-filters');
      if (e.target.value === 'clients' || e.target.value === 'specific') {
        filters.classList.remove('hidden');
      } else {
        filters.classList.add('hidden');
      }
    });
  }

  // Cancel button
  const cancelRuleBtn = document.getElementById('cancel-rule-btn');
  if (cancelRuleBtn) {
    cancelRuleBtn.addEventListener('click', () => {
      closeRuleModal();
    });
  }
}

function updateTriggerOptions(ruleType) {
  const triggerEvent = document.getElementById('rule-trigger-event');
  const conditions = document.getElementById('trigger-conditions');
  
  if (!triggerEvent) return;

  // Update trigger event options based on rule type
  if (ruleType === 'session_reminder') {
    triggerEvent.innerHTML = `
      <option value="session_created">Session Created</option>
      <option value="session_scheduled">Session Scheduled</option>
    `;
    conditions.classList.remove('hidden');
  } else if (ruleType === 'payment_reminder') {
    triggerEvent.innerHTML = `
      <option value="payment_due">Payment Due</option>
      <option value="payment_overdue">Payment Overdue</option>
    `;
    conditions.classList.add('hidden');
  } else if (ruleType === 'birthday') {
    triggerEvent.innerHTML = `
      <option value="birthday">Birthday</option>
    `;
    conditions.classList.add('hidden');
  } else {
    triggerEvent.innerHTML = `
      <option value="session_created">Session Created</option>
      <option value="payment_due">Payment Due</option>
      <option value="birthday">Birthday</option>
      <option value="inactivity">Inactivity</option>
    `;
    conditions.classList.add('hidden');
  }
}

async function loadRules() {
  try {
    const response = await automationAPI.getRules();
    rules = response.data.rules || [];
    renderRules();
  } catch (error) {
    console.error('Error loading rules:', error);
    showToast('Failed to load rules', 'error');
  }
}

function renderRules() {
  const container = document.getElementById('rules-list');
  if (!container) return;

  if (rules.length === 0) {
    container.innerHTML = '<div class="text-center text-gray-500 py-8">No automation rules yet. Create your first rule!</div>';
    return;
  }

  container.innerHTML = rules.map(rule => `
    <div class="border border-gray-200 rounded-lg p-6 hover:bg-gray-50">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center space-x-3 mb-2">
            <h3 class="text-lg font-semibold text-gray-900">${escapeHtml(rule.name)}</h3>
            <span class="px-3 py-1 rounded-full text-xs font-medium ${
              rule.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            }">${rule.enabled ? 'Enabled' : 'Disabled'}</span>
            <span class="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">${escapeHtml(rule.rule_type)}</span>
          </div>
          ${rule.description ? `<p class="text-sm text-gray-600 mb-2">${escapeHtml(rule.description)}</p>` : ''}
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div>
              <p class="text-xs text-gray-500">Executions</p>
              <p class="text-lg font-semibold">${rule.run_count || 0}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Success</p>
              <p class="text-lg font-semibold text-green-600">${rule.success_count || 0}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Failed</p>
              <p class="text-lg font-semibold text-red-600">${rule.failure_count || 0}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Last Run</p>
              <p class="text-sm font-medium">${rule.last_run_at ? formatDateTime(rule.last_run_at) : 'Never'}</p>
            </div>
          </div>
        </div>
        <div class="ml-4 flex flex-col space-y-2">
          <button onclick="toggleRule(${rule.id})" class="bg-${rule.enabled ? 'yellow' : 'green'}-500 hover:bg-${rule.enabled ? 'yellow' : 'green'}-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            ${rule.enabled ? 'Disable' : 'Enable'}
          </button>
          <button onclick="executeRule(${rule.id})" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            Run Now
          </button>
          <button onclick="editRule(${rule.id})" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            Edit
          </button>
          <button onclick="deleteRule(${rule.id})" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            Delete
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

async function loadLogs() {
  try {
    const response = await automationAPI.getLogs({ page: 1, per_page: 50 });
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
    container.innerHTML = '<div class="text-center text-gray-500 py-8">No execution logs yet</div>';
    return;
  }

  container.innerHTML = logs.map(log => `
    <div class="border border-gray-200 rounded-lg p-4">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <p class="font-medium text-gray-900">Rule ID: ${log.rule_id}</p>
          <p class="text-sm text-gray-600 mt-1">Executed: ${formatDateTime(log.executed_at)}</p>
          <p class="text-sm text-gray-600">Recipients: ${log.recipients_count || 0} | Sent: ${log.sent_count || 0} | Failed: ${log.failed_count || 0}</p>
          ${log.error_message ? `<p class="text-sm text-red-600 mt-1">Error: ${escapeHtml(log.error_message)}</p>` : ''}
        </div>
        <div class="ml-4">
          <span class="px-3 py-1 rounded-full text-xs font-medium ${
            log.status === 'success' ? 'bg-green-100 text-green-800' :
            log.status === 'failed' ? 'bg-red-100 text-red-800' :
            'bg-yellow-100 text-yellow-800'
          }">${escapeHtml(log.status)}</span>
        </div>
      </div>
    </div>
  `).join('');
}

async function loadAnalytics() {
  try {
    const response = await automationAPI.getAnalytics();
    renderAnalytics(response.data);
  } catch (error) {
    console.error('Error loading analytics:', error);
  }
}

function renderAnalytics(data) {
  const container = document.getElementById('analytics-content');
  if (!container) return;

  container.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-gradient-to-br from-orange-400 to-orange-600 rounded-lg p-6 text-white">
        <h3 class="text-sm font-medium opacity-90">Total Executions</h3>
        <p class="text-3xl font-bold mt-2">${data.total_executions || 0}</p>
      </div>
      <div class="bg-gradient-to-br from-green-400 to-green-600 rounded-lg p-6 text-white">
        <h3 class="text-sm font-medium opacity-90">Success Rate</h3>
        <p class="text-3xl font-bold mt-2">${data.success_rate || 0}%</p>
      </div>
      <div class="bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg p-6 text-white">
        <h3 class="text-sm font-medium opacity-90">Total Actions Sent</h3>
        <p class="text-3xl font-bold mt-2">${data.total_actions_sent || 0}</p>
      </div>
      <div class="bg-gradient-to-br from-purple-400 to-purple-600 rounded-lg p-6 text-white">
        <h3 class="text-sm font-medium opacity-90">Success / Failure</h3>
        <p class="text-lg mt-2">Success: ${data.success_count || 0}</p>
        <p class="text-lg">Failure: ${data.failure_count || 0}</p>
      </div>
    </div>
    ${data.rule_performance && data.rule_performance.length > 0 ? `
      <div class="mt-6">
        <h3 class="text-lg font-semibold mb-4">Rule Performance</h3>
        <div class="space-y-2">
          ${data.rule_performance.map(rule => `
            <div class="border border-gray-200 rounded-lg p-4">
              <div class="flex items-center justify-between">
                <span class="font-medium">${escapeHtml(rule.rule_name)}</span>
                <div class="flex items-center space-x-4">
                  <span class="text-sm text-gray-600">Executions: ${rule.executions}</span>
                  <span class="text-sm text-gray-600">Sent: ${rule.sent}</span>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    ` : ''}
  `;
}

function openRuleModal(ruleId = null) {
  currentRuleId = ruleId;
  const modal = document.getElementById('rule-modal');
  
  if (ruleId) {
    const rule = rules.find(r => r.id === ruleId);
    if (rule) {
      document.getElementById('rule-modal-title').textContent = 'Edit Rule';
      document.getElementById('rule-name').value = rule.name;
      document.getElementById('rule-description').value = rule.description || '';
      document.getElementById('rule-type').value = rule.rule_type;
      document.getElementById('rule-trigger-event').value = rule.trigger_event || '';
      document.getElementById('rule-action-type').value = rule.action_type;
      document.getElementById('rule-message').value = rule.custom_message || '';
      document.getElementById('rule-target').value = rule.target_audience || 'all';
      document.getElementById('rule-enabled').checked = rule.enabled;
      
      updateTriggerOptions(rule.rule_type);
      
      if (rule.trigger_conditions && rule.trigger_conditions.hours_before) {
        document.getElementById('hours-before').value = rule.trigger_conditions.hours_before;
      }
    }
  } else {
    document.getElementById('rule-modal-title').textContent = 'New Automation Rule';
    document.getElementById('rule-form').reset();
    document.getElementById('rule-enabled').checked = true;
    updateTriggerOptions('session_reminder');
  }
  
  modal.classList.remove('hidden');
}

function closeRuleModal() {
  document.getElementById('rule-modal').classList.add('hidden');
  currentRuleId = null;
  document.getElementById('rule-form').reset();
}

async function saveRule() {
  const name = document.getElementById('rule-name').value.trim();
  const description = document.getElementById('rule-description').value.trim();
  const ruleType = document.getElementById('rule-type').value;
  const triggerEvent = document.getElementById('rule-trigger-event').value;
  const actionType = document.getElementById('rule-action-type').value;
  const customMessage = document.getElementById('rule-message').value.trim();
  const targetAudience = document.getElementById('rule-target').value;
  const enabled = document.getElementById('rule-enabled').checked;
  const hoursBefore = document.getElementById('hours-before').value;

  if (!name || !ruleType || !triggerEvent) {
    showToast('Please fill in all required fields', 'error');
    return;
  }

  const triggerConditions = {};
  if (hoursBefore) {
    triggerConditions.hours_before = parseInt(hoursBefore);
  }

  const targetFilters = {};
  if (targetAudience === 'clients') {
    const status = document.getElementById('target-status').value;
    if (status) targetFilters.status = status;
  }

  const ruleData = {
    name,
    description,
    rule_type: ruleType,
    trigger_event: triggerEvent,
    trigger_conditions: triggerConditions,
    action_type: actionType,
    custom_message: customMessage || null,
    target_audience: targetAudience,
    target_filters: targetFilters,
    enabled
  };

  try {
    if (currentRuleId) {
      await automationAPI.updateRule(currentRuleId, ruleData);
      showToast('Rule updated successfully', 'success');
    } else {
      await automationAPI.createRule(ruleData);
      showToast('Rule created successfully', 'success');
    }
    
    closeRuleModal();
    loadRules();
  } catch (error) {
    console.error('Error saving rule:', error);
    showToast('Failed to save rule', 'error');
  }
}

async function toggleRule(id) {
  try {
    await automationAPI.toggleRule(id);
    showToast('Rule toggled successfully', 'success');
    loadRules();
  } catch (error) {
    console.error('Error toggling rule:', error);
    showToast('Failed to toggle rule', 'error');
  }
}

async function executeRule(id) {
  if (!confirm('Are you sure you want to execute this rule now?')) return;

  try {
    const response = await automationAPI.executeRule(id);
    showToast(`Rule executed: ${response.data.result.sent} sent, ${response.data.result.failed} failed`, 'success');
    loadRules();
    loadLogs();
    loadAnalytics();
  } catch (error) {
    console.error('Error executing rule:', error);
    showToast('Failed to execute rule', 'error');
  }
}

function editRule(id) {
  openRuleModal(id);
}

async function deleteRule(id) {
  if (!confirm('Are you sure you want to delete this rule?')) return;

  try {
    await automationAPI.deleteRule(id);
    showToast('Rule deleted successfully', 'success');
    loadRules();
  } catch (error) {
    console.error('Error deleting rule:', error);
    showToast('Failed to delete rule', 'error');
  }
}

// Make functions available globally
window.toggleRule = toggleRule;
window.executeRule = executeRule;
window.editRule = editRule;
window.deleteRule = deleteRule;

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

