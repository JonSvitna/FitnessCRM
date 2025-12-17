/**
 * Email Campaign Builder Interface
 * Phase 5: Communication - M5.3: Email Campaigns Frontend
 */

import { campaignAPI } from './api.js';
import { showToast } from './main.js';

// Global state
let campaigns = [];
let templates = [];
let currentCampaignId = null;
let currentTemplateId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initializeSidebar();
  setupTabs();
  setupEventListeners();
  loadCampaigns();
  loadTemplates();
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
  const tabs = ['campaigns', 'templates'];
  
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
  // New campaign button
  const newCampaignBtn = document.getElementById('new-campaign-btn');
  if (newCampaignBtn) {
    newCampaignBtn.addEventListener('click', () => {
      openCampaignModal();
    });
  }

  // Campaign form
  const campaignForm = document.getElementById('campaign-form');
  if (campaignForm) {
    campaignForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await saveCampaign();
    });
  }

  // A/B test checkbox
  const abTestCheckbox = document.getElementById('campaign-ab-test');
  if (abTestCheckbox) {
    abTestCheckbox.addEventListener('change', (e) => {
      const fields = document.getElementById('ab-test-fields');
      if (e.target.checked) {
        fields.classList.remove('hidden');
      } else {
        fields.classList.add('hidden');
      }
    });
  }

  // Send now checkbox
  const sendNowCheckbox = document.getElementById('campaign-send-now');
  if (sendNowCheckbox) {
    sendNowCheckbox.addEventListener('change', (e) => {
      const scheduleFields = document.getElementById('schedule-fields');
      if (e.target.checked) {
        scheduleFields.classList.add('hidden');
      } else {
        scheduleFields.classList.remove('hidden');
      }
    });
  }

  // Segment type change
  const segmentType = document.getElementById('campaign-segment-type');
  if (segmentType) {
    segmentType.addEventListener('change', (e) => {
      const customFilters = document.getElementById('custom-filters');
      if (e.target.value === 'custom') {
        customFilters.classList.remove('hidden');
      } else {
        customFilters.classList.add('hidden');
      }
    });
  }

  // Template selection
  const templateSelect = document.getElementById('campaign-template');
  if (templateSelect) {
    templateSelect.addEventListener('change', (e) => {
      if (e.target.value) {
        const template = templates.find(t => t.id === parseInt(e.target.value));
        if (template) {
          document.getElementById('campaign-subject').value = template.subject;
          document.getElementById('campaign-html-body').value = template.html_body;
          document.getElementById('campaign-text-body').value = template.text_body || '';
        }
      }
    });
  }

  // Cancel buttons
  const cancelCampaignBtn = document.getElementById('cancel-campaign-btn');
  if (cancelCampaignBtn) {
    cancelCampaignBtn.addEventListener('click', () => {
      closeCampaignModal();
    });
  }

  // Email template form
  const emailTemplateForm = document.getElementById('email-template-form');
  if (emailTemplateForm) {
    emailTemplateForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await saveEmailTemplate();
    });
  }

  // New email template button
  const newEmailTemplateBtn = document.getElementById('new-email-template-btn');
  if (newEmailTemplateBtn) {
    newEmailTemplateBtn.addEventListener('click', () => {
      openEmailTemplateModal();
    });
  }

  // Cancel email template
  const cancelEmailTemplateBtn = document.getElementById('cancel-email-template-btn');
  if (cancelEmailTemplateBtn) {
    cancelEmailTemplateBtn.addEventListener('click', () => {
      closeEmailTemplateModal();
    });
  }
}

async function loadCampaigns() {
  try {
    const response = await campaignAPI.getCampaigns({ page: 1, per_page: 50 });
    campaigns = response.data.campaigns || [];
    renderCampaigns();
  } catch (error) {
    console.error('Error loading campaigns:', error);
    showToast('Failed to load campaigns', 'error');
  }
}

function renderCampaigns() {
  const container = document.getElementById('campaigns-list');
  if (!container) return;

  if (campaigns.length === 0) {
    container.innerHTML = '<div class="text-center text-gray-500 py-8">No campaigns yet. Create your first campaign!</div>';
    return;
  }

  container.innerHTML = campaigns.map(campaign => `
    <div class="border border-gray-200 rounded-lg p-6 hover:bg-gray-50">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center space-x-3 mb-2">
            <h3 class="text-lg font-semibold text-gray-900">${escapeHtml(campaign.name)}</h3>
            <span class="px-3 py-1 rounded-full text-xs font-medium ${
              campaign.status === 'sent' ? 'bg-green-100 text-green-800' :
              campaign.status === 'sending' ? 'bg-blue-100 text-blue-800' :
              campaign.status === 'scheduled' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }">${escapeHtml(campaign.status)}</span>
          </div>
          ${campaign.description ? `<p class="text-sm text-gray-600 mb-2">${escapeHtml(campaign.description)}</p>` : ''}
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div>
              <p class="text-xs text-gray-500">Recipients</p>
              <p class="text-lg font-semibold">${campaign.total_recipients || 0}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Sent</p>
              <p class="text-lg font-semibold">${campaign.emails_sent || 0}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Opened</p>
              <p class="text-lg font-semibold">${campaign.emails_opened || 0}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500">Clicked</p>
              <p class="text-lg font-semibold">${campaign.emails_clicked || 0}</p>
            </div>
          </div>
        </div>
        <div class="ml-4 flex flex-col space-y-2">
          ${campaign.status === 'draft' || campaign.status === 'scheduled' ? `
            <button onclick="sendCampaign(${campaign.id})" class="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Send
            </button>
            <button onclick="editCampaign(${campaign.id})" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Edit
            </button>
            <button onclick="cancelCampaign(${campaign.id})" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Cancel
            </button>
          ` : ''}
          <button onclick="viewCampaignAnalytics(${campaign.id})" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            Analytics
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

async function loadTemplates() {
  try {
    const response = await campaignAPI.getTemplates();
    templates = response.data.templates || [];
    renderEmailTemplates();
    populateTemplateSelect();
  } catch (error) {
    console.error('Error loading templates:', error);
  }
}

function renderEmailTemplates() {
  const container = document.getElementById('email-templates-list');
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
          <p class="text-sm text-gray-700 mt-2 font-medium">${escapeHtml(template.subject)}</p>
        </div>
        <div class="flex items-center space-x-2 ml-4">
          <button onclick="useEmailTemplate(${template.id})" class="text-orange-500 hover:text-orange-600 px-3 py-1 rounded text-sm font-medium">
            Use
          </button>
          <button onclick="editEmailTemplate(${template.id})" class="text-gray-600 hover:text-gray-800 px-3 py-1 rounded text-sm font-medium">
            Edit
          </button>
          <button onclick="deleteEmailTemplate(${template.id})" class="text-red-500 hover:text-red-600 px-3 py-1 rounded text-sm font-medium">
            Delete
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

function populateTemplateSelect() {
  const select = document.getElementById('campaign-template');
  if (!select) return;

  select.innerHTML = '<option value="">Create custom email</option>';
  templates.forEach(template => {
    const option = document.createElement('option');
    option.value = template.id;
    option.textContent = template.name;
    select.appendChild(option);
  });
}

function openCampaignModal(campaignId = null) {
  currentCampaignId = campaignId;
  const modal = document.getElementById('campaign-modal');
  
  if (campaignId) {
    const campaign = campaigns.find(c => c.id === campaignId);
    if (campaign) {
      document.getElementById('campaign-modal-title').textContent = 'Edit Campaign';
      document.getElementById('campaign-name').value = campaign.name;
      document.getElementById('campaign-description').value = campaign.description || '';
      document.getElementById('campaign-subject').value = campaign.subject;
      document.getElementById('campaign-html-body').value = campaign.html_body;
      document.getElementById('campaign-text-body').value = campaign.text_body || '';
      document.getElementById('campaign-segment-type').value = campaign.segment_type;
      document.getElementById('campaign-ab-test').checked = campaign.ab_test_enabled;
      if (campaign.ab_test_enabled) {
        document.getElementById('ab-test-fields').classList.remove('hidden');
        document.getElementById('campaign-subject-a').value = campaign.ab_test_subject_a || '';
        document.getElementById('campaign-subject-b').value = campaign.ab_test_subject_b || '';
        document.getElementById('campaign-split').value = campaign.ab_test_split_percentage || 50;
      }
    }
  } else {
    document.getElementById('campaign-modal-title').textContent = 'New Campaign';
    document.getElementById('campaign-form').reset();
    document.getElementById('ab-test-fields').classList.add('hidden');
    document.getElementById('schedule-fields').classList.add('hidden');
    document.getElementById('custom-filters').classList.add('hidden');
  }
  
  modal.classList.remove('hidden');
}

function closeCampaignModal() {
  document.getElementById('campaign-modal').classList.add('hidden');
  currentCampaignId = null;
  document.getElementById('campaign-form').reset();
}

async function saveCampaign() {
  const name = document.getElementById('campaign-name').value.trim();
  const description = document.getElementById('campaign-description').value.trim();
  const subject = document.getElementById('campaign-subject').value.trim();
  const htmlBody = document.getElementById('campaign-html-body').value.trim();
  const textBody = document.getElementById('campaign-text-body').value.trim();
  const templateId = document.getElementById('campaign-template').value || null;
  const segmentType = document.getElementById('campaign-segment-type').value;
  const abTestEnabled = document.getElementById('campaign-ab-test').checked;
  const sendNow = document.getElementById('campaign-send-now').checked;
  const scheduledAt = document.getElementById('campaign-scheduled-at').value;

  if (!name || !subject || !htmlBody) {
    showToast('Please fill in all required fields', 'error');
    return;
  }

  // Build segment filters
  const segmentFilters = {};
  if (segmentType === 'custom') {
    const status = document.getElementById('filter-status').value;
    const membership = document.getElementById('filter-membership').value;
    if (status) segmentFilters.status = status;
    if (membership) segmentFilters.membership_type = membership;
  }

  const campaignData = {
    name,
    description,
    subject,
    html_body: htmlBody,
    text_body: textBody,
    template_id: templateId ? parseInt(templateId) : null,
    segment_type: segmentType,
    segment_filters: segmentFilters,
    ab_test_enabled: abTestEnabled,
    send_immediately: sendNow
  };

  if (abTestEnabled) {
    campaignData.ab_test_subject_a = document.getElementById('campaign-subject-a').value.trim();
    campaignData.ab_test_subject_b = document.getElementById('campaign-subject-b').value.trim();
    campaignData.ab_test_split_percentage = parseInt(document.getElementById('campaign-split').value) || 50;
  }

  if (!sendNow && scheduledAt) {
    campaignData.scheduled_at = scheduledAt;
  }

  try {
    if (currentCampaignId) {
      await campaignAPI.updateCampaign(currentCampaignId, campaignData);
      showToast('Campaign updated successfully', 'success');
    } else {
      await campaignAPI.createCampaign(campaignData);
      showToast('Campaign created successfully', 'success');
    }
    
    closeCampaignModal();
    loadCampaigns();
  } catch (error) {
    console.error('Error saving campaign:', error);
    showToast('Failed to save campaign', 'error');
  }
}

async function sendCampaign(id) {
  if (!confirm('Are you sure you want to send this campaign?')) return;

  try {
    await campaignAPI.sendCampaign(id);
    showToast('Campaign sending started', 'success');
    loadCampaigns();
  } catch (error) {
    console.error('Error sending campaign:', error);
    showToast('Failed to send campaign', 'error');
  }
}

async function cancelCampaign(id) {
  if (!confirm('Are you sure you want to cancel this campaign?')) return;

  try {
    await campaignAPI.cancelCampaign(id);
    showToast('Campaign cancelled', 'success');
    loadCampaigns();
  } catch (error) {
    console.error('Error cancelling campaign:', error);
    showToast('Failed to cancel campaign', 'error');
  }
}

async function viewCampaignAnalytics(id) {
  try {
    const response = await campaignAPI.getAnalytics(id);
    const analytics = response.data;
    
    const message = `
      Campaign Analytics:
      
      Total Recipients: ${analytics.total_recipients}
      Emails Sent: ${analytics.emails_sent}
      Emails Delivered: ${analytics.emails_delivered}
      Emails Opened: ${analytics.emails_opened} (${analytics.open_rate}%)
      Emails Clicked: ${analytics.emails_clicked} (${analytics.click_rate}%)
      Delivery Rate: ${analytics.delivery_rate}%
      Bounce Rate: ${analytics.bounce_rate}%
    `;
    
    alert(message);
  } catch (error) {
    console.error('Error loading analytics:', error);
    showToast('Failed to load analytics', 'error');
  }
}

function editCampaign(id) {
  openCampaignModal(id);
}

function openEmailTemplateModal(templateId = null) {
  currentTemplateId = templateId;
  const modal = document.getElementById('email-template-modal');
  
  if (templateId) {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      document.getElementById('email-template-modal-title').textContent = 'Edit Template';
      document.getElementById('email-template-name').value = template.name;
      document.getElementById('email-template-category').value = template.category || 'custom';
      document.getElementById('email-template-subject').value = template.subject;
      document.getElementById('email-template-html').value = template.html_body;
      document.getElementById('email-template-text').value = template.text_body || '';
    }
  } else {
    document.getElementById('email-template-modal-title').textContent = 'New Email Template';
    document.getElementById('email-template-form').reset();
  }
  
  modal.classList.remove('hidden');
}

function closeEmailTemplateModal() {
  document.getElementById('email-template-modal').classList.add('hidden');
  currentTemplateId = null;
  document.getElementById('email-template-form').reset();
}

async function saveEmailTemplate() {
  const name = document.getElementById('email-template-name').value.trim();
  const category = document.getElementById('email-template-category').value;
  const subject = document.getElementById('email-template-subject').value.trim();
  const htmlBody = document.getElementById('email-template-html').value.trim();
  const textBody = document.getElementById('email-template-text').value.trim();

  if (!name || !subject || !htmlBody) {
    showToast('Please fill in all required fields', 'error');
    return;
  }

  try {
    if (currentTemplateId) {
      await campaignAPI.updateTemplate(currentTemplateId, { name, category, subject, html_body: htmlBody, text_body: textBody });
      showToast('Template updated successfully', 'success');
    } else {
      await campaignAPI.createTemplate({ name, category, subject, html_body: htmlBody, text_body: textBody });
      showToast('Template created successfully', 'success');
    }
    
    closeEmailTemplateModal();
    loadTemplates();
  } catch (error) {
    console.error('Error saving template:', error);
    showToast('Failed to save template', 'error');
  }
}

function useEmailTemplate(id) {
  const template = templates.find(t => t.id === id);
  if (template) {
    document.getElementById('campaign-template').value = id;
    document.getElementById('campaign-subject').value = template.subject;
    document.getElementById('campaign-html-body').value = template.html_body;
    document.getElementById('campaign-text-body').value = template.text_body || '';
    document.getElementById('tab-campaigns').click();
    document.getElementById('new-campaign-btn').click();
  }
}

function editEmailTemplate(id) {
  openEmailTemplateModal(id);
}

async function deleteEmailTemplate(id) {
  if (!confirm('Are you sure you want to delete this template?')) return;

  try {
    await campaignAPI.deleteTemplate(id);
    showToast('Template deleted successfully', 'success');
    loadTemplates();
  } catch (error) {
    console.error('Error deleting template:', error);
    showToast('Failed to delete template', 'error');
  }
}

// Make functions available globally
window.sendCampaign = sendCampaign;
window.cancelCampaign = cancelCampaign;
window.viewCampaignAnalytics = viewCampaignAnalytics;
window.editCampaign = editCampaign;
window.useEmailTemplate = useEmailTemplate;
window.editEmailTemplate = editEmailTemplate;
window.deleteEmailTemplate = deleteEmailTemplate;

// Utility functions
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

