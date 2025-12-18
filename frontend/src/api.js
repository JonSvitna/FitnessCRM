import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor to handle offline errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If offline and it's a POST/PUT/DELETE request, queue it
    if (!navigator.onLine && error.config && ['post', 'put', 'delete'].includes(error.config.method?.toLowerCase())) {
      const config = error.config;
      const actionType = getActionTypeFromUrl(config.url, config.method);
      
      if (actionType) {
        // Dynamically import to avoid circular dependency
        const { queueOfflineAction } = await import('./offline.js');
        queueOfflineAction(
          actionType,
          config.data ? JSON.parse(config.data) : {},
          extractIdFromUrl(config.url),
          extractThreadIdFromUrl(config.url)
        );
        
        // Return a fake success response so the UI doesn't break
        return Promise.resolve({
          data: { 
            success: true, 
            message: 'Action queued for sync when online',
            queued: true 
          },
          status: 202,
          statusText: 'Accepted',
          headers: {},
          config: config
        });
      }
    }
    
    return Promise.reject(error);
  }
);

// Helper function to determine action type from URL and method
function getActionTypeFromUrl(url, method) {
  if (!url || !method) return null;
  
  const lowerMethod = method.toLowerCase();
  const lowerUrl = url.toLowerCase();
  
  if (lowerUrl.includes('/api/clients')) {
    if (lowerMethod === 'post') return 'create_client';
    if (lowerMethod === 'put') return 'update_client';
  }
  
  if (lowerUrl.includes('/api/trainers')) {
    if (lowerMethod === 'post') return 'create_trainer';
    if (lowerMethod === 'put') return 'update_trainer';
  }
  
  if (lowerUrl.includes('/sessions') && lowerMethod === 'post') {
    return 'create_session';
  }
  
  if (lowerUrl.includes('/api/messages/threads') && lowerUrl.includes('/messages') && lowerMethod === 'post') {
    return 'create_message';
  }
  
  if (lowerUrl.includes('/api/sms/send') && lowerMethod === 'post') {
    return 'send_sms';
  }
  
  return null;
}

// Helper function to extract ID from URL
function extractIdFromUrl(url) {
  const match = url.match(/\/(\d+)(?:\/|$)/);
  return match ? parseInt(match[1]) : null;
}

// Helper function to extract thread ID from URL
function extractThreadIdFromUrl(url) {
  const match = url.match(/\/threads\/(\d+)/);
  return match ? parseInt(match[1]) : null;
}

// Trainer API
export const trainerAPI = {
  create: (data) => api.post('/api/trainers', data),
  getAll: (params = {}) => api.get('/api/trainers', { params }),
  getById: (id) => api.get(`/api/trainers/${id}`),
  update: (id, data) => api.put(`/api/trainers/${id}`, data),
  delete: (id) => api.delete(`/api/trainers/${id}`),
};

// Client API
export const clientAPI = {
  create: (data) => api.post('/api/clients', data),
  getAll: (params = {}) => api.get('/api/clients', { params }),
  getById: (id) => api.get(`/api/clients/${id}`),
  update: (id, data) => api.put(`/api/clients/${id}`, data),
  delete: (id) => api.delete(`/api/clients/${id}`),
};

// CRM API
export const crmAPI = {
  getDashboard: () => api.get('/api/crm/dashboard'),
  getStats: () => api.get('/api/crm/stats'),
  assignClientToTrainer: (data) => api.post('/api/crm/assign', data),
  getAssignments: () => api.get('/api/crm/assignments'),
};

// Settings API
export const settingsAPI = {
  get: () => api.get('/api/settings'),
  create: (data) => api.post('/api/settings', data),
  update: (data) => api.put('/api/settings', data),
  testSendGrid: () => api.post('/api/settings/test-sendgrid'),
  testTwilio: () => api.post('/api/settings/test-twilio'),
};

// Integrations API
export const integrationsAPI = {
  getStatus: () => api.get('/api/integrations/status'),
  googleCalendarAuth: () => api.get('/api/integrations/google-calendar/auth'),
  googleCalendarSync: (data) => api.post('/api/integrations/google-calendar/sync', data),
  zoomGenerateLink: (data) => api.post('/api/integrations/zoom/generate-link', data),
  myfitnesspalConnect: (data) => api.post('/api/integrations/myfitnesspal/connect', data),
  listWebhooks: () => api.get('/api/integrations/webhooks'),
  createWebhook: (data) => api.post('/api/integrations/webhooks', data),
  deleteWebhook: (id) => api.delete(`/api/integrations/webhooks/${id}`),
};

// Advanced Analytics API
export const advancedAnalyticsAPI = {
  getChurnPrediction: (clientId, daysLookback = 90) => 
    api.get(`/api/analytics/advanced/churn-prediction/${clientId}`, { params: { days_lookback: daysLookback } }),
  getBatchChurnPredictions: (clientIds) => 
    api.post('/api/analytics/advanced/churn-prediction/batch', { client_ids: clientIds }),
  getRevenueForecast: (months = 6) => 
    api.get('/api/analytics/advanced/revenue-forecast', { params: { months } }),
  getTrainerBenchmark: (trainerId) => 
    api.get(`/api/analytics/advanced/trainer-benchmark/${trainerId}`),
  getAllTrainerBenchmarks: () => 
    api.get('/api/analytics/advanced/trainer-benchmark/all'),
  getPredictiveInsights: (daysLookback = 30) => 
    api.get('/api/analytics/advanced/predictive-insights', { params: { days_lookback: daysLookback } }),
};

// Activity API
export const activityAPI = {
  getRecent: (limit = 50) => api.get(`/api/activity/recent?limit=${limit}`),
  getAll: (params) => api.get('/api/activity', { params }),
  getStats: () => api.get('/api/activity/stats'),
};

// Session API
export const sessionAPI = {
  create: (data) => api.post('/sessions', data),
  getAll: (params = {}) => api.get('/sessions', { params }),
  getById: (id) => api.get(`/sessions/${id}`),
  update: (id, data) => api.put(`/sessions/${id}`, data),
  delete: (id) => api.delete(`/sessions/${id}`),
  exportIcal: (params = {}) => {
    // Build query string
    const queryParams = new URLSearchParams(params).toString();
    const url = `${API_BASE_URL}/sessions/export/ical${queryParams ? '?' + queryParams : ''}`;
    
    // Trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = 'fitnesscrm-sessions.ics';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

// Recurring Session API
export const recurringSessionAPI = {
  create: (data) => api.post('/recurring-sessions', data),
  getAll: (params = {}) => api.get('/recurring-sessions', { params }),
  delete: (id, deleteFuture = false) => api.delete(`/recurring-sessions/${id}?delete_future=${deleteFuture}`),
};

// Measurement API
export const measurementAPI = {
  create: (data) => api.post('/measurements', data),
  getAll: (params = {}) => api.get('/measurements', { params }),
  getById: (id) => api.get(`/measurements/${id}`),
  update: (id, data) => api.put(`/measurements/${id}`, data),
  delete: (id) => api.delete(`/measurements/${id}`),
  getLatest: (clientId) => api.get(`/measurements/client/${clientId}/latest`),
  getProgress: (clientId) => api.get(`/measurements/client/${clientId}/progress`),
};

// File API
export const fileAPI = {
  upload: (formData) => {
    return api.post('/files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getAll: (params = {}) => api.get('/files', { params }),
  getById: (id) => api.get(`/files/${id}`),
  update: (id, data) => api.put(`/files/${id}`, data),
  delete: (id) => api.delete(`/files/${id}`),
  download: (id, filename) => {
    const url = `${API_BASE_URL}/files/${id}/download`;
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
  getCategories: () => api.get('/files/categories'),
  getStats: (params = {}) => api.get('/files/stats', { params }),
};

// Exercise API
export const exerciseAPI = {
  create: (data) => api.post('/api/workouts/exercises', data),
  getAll: (params = {}) => api.get('/api/workouts/exercises', { params }),
  getById: (id) => api.get(`/api/workouts/exercises/${id}`),
  update: (id, data) => api.put(`/api/workouts/exercises/${id}`, data),
  delete: (id) => api.delete(`/api/workouts/exercises/${id}`),
  getCategories: () => api.get('/api/workouts/exercises/categories'),
  getMuscleGroups: () => api.get('/api/workouts/exercises/muscle-groups'),
  getEquipment: () => api.get('/api/workouts/exercises/equipment'),
  seed: () => api.post('/api/workouts/exercises/seed'),
};

// Workout API
export const workoutAPI = {
  // Templates
  createTemplate: (data) => api.post('/api/workouts/templates', data),
  getAllTemplates: (params = {}) => api.get('/api/workouts/templates', { params }),
  getTemplate: (id) => api.get(`/api/workouts/templates/${id}`),
  updateTemplate: (id, data) => api.put(`/api/workouts/templates/${id}`, data),
  deleteTemplate: (id) => api.delete(`/api/workouts/templates/${id}`),
  
  // Assignments
  assignWorkout: (data) => api.post('/api/workouts/assign', data),
  getClientAssignments: (clientId, params = {}) => api.get(`/api/workouts/assignments/${clientId}`, { params }),
  updateAssignment: (id, data) => api.put(`/api/workouts/assignments/${id}`, data),
  
  // Logging
  logWorkout: (data) => api.post('/api/workouts/log', data),
  getClientLogs: (clientId, params = {}) => api.get(`/api/workouts/logs/${clientId}`, { params }),
  
  // Categories
  getCategories: () => api.get('/api/workouts/categories'),
};

// Progress Photo API
export const progressPhotoAPI = {
  upload: (formData) => {
    return api.post('/progress-photos', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getAll: (params = {}) => api.get('/progress-photos', { params }),
  getById: (id) => api.get(`/progress-photos/${id}`),
  update: (id, data) => api.put(`/progress-photos/${id}`, data),
  delete: (id) => api.delete(`/progress-photos/${id}`),
  getFile: (id) => `${API_BASE_URL}/progress-photos/${id}/file`,
  getComparison: (clientId) => api.get(`/progress-photos/client/${clientId}/comparison`),
};

// Goal API
export const goalAPI = {
  create: (data) => api.post('/goals', data),
  getAll: (params = {}) => api.get('/goals', { params }),
  getById: (id) => api.get(`/goals/${id}`),
  update: (id, data) => api.put(`/goals/${id}`, data),
  delete: (id) => api.delete(`/goals/${id}`),
  getSummary: (clientId) => api.get(`/goals/client/${clientId}/summary`),
  
  // Milestones
  createMilestone: (goalId, data) => api.post(`/goals/${goalId}/milestones`, data),
  updateMilestone: (goalId, milestoneId, data) => api.put(`/goals/${goalId}/milestones/${milestoneId}`, data),
  deleteMilestone: (goalId, milestoneId) => api.delete(`/goals/${goalId}/milestones/${milestoneId}`),
};

// Message API
export const messageAPI = {
  // Threads
  getThreads: (params) => api.get('/api/messages/threads', { params }),
  createThread: (data) => api.post('/api/messages/threads', data),
  getThread: (threadId, params) => api.get(`/api/messages/threads/${threadId}`, { params }),
  archiveThread: (threadId, data) => api.put(`/api/messages/threads/${threadId}/archive`, data),
  
  // Messages
  createMessage: (threadId, data) => api.post(`/api/messages/threads/${threadId}/messages`, data),
  markMessageRead: (messageId, data) => api.put(`/api/messages/messages/${messageId}/read`, data),
  markThreadRead: (threadId, data) => api.put(`/api/messages/threads/${threadId}/read`, data),
  deleteMessage: (messageId, data) => api.delete(`/api/messages/messages/${messageId}`, { data }),
  
  // Search and utilities
  searchMessages: (params) => api.get('/api/messages/search', { params }),
  getUnreadCount: (params) => api.get('/api/messages/unread-count', { params }),
};

// SMS API
export const smsAPI = {
  // Send SMS
  send: (data) => api.post('/api/sms/send', data),
  
  // Templates
  getTemplates: (params) => api.get('/api/sms/templates', { params }),
  createTemplate: (data) => api.post('/api/sms/templates', data),
  updateTemplate: (id, data) => api.put(`/api/sms/templates/${id}`, data),
  deleteTemplate: (id) => api.delete(`/api/sms/templates/${id}`),
  sendTemplate: (id, data) => api.post(`/api/sms/templates/${id}/send`, data),
  
  // Logs
  getLogs: (params) => api.get('/api/sms/logs', { params }),
  
  // Schedules
  getSchedules: (params) => api.get('/api/sms/schedules', { params }),
  createSchedule: (data) => api.post('/api/sms/schedules', data),
  cancelSchedule: (id) => api.delete(`/api/sms/schedules/${id}`),
  
  // Analytics
  getAnalytics: (params) => api.get('/api/sms/analytics', { params }),
};

// Campaign API
export const campaignAPI = {
  // Campaigns
  getCampaigns: (params) => api.get('/api/campaigns', { params }),
  createCampaign: (data) => api.post('/api/campaigns', data),
  getCampaign: (id) => api.get(`/api/campaigns/${id}`),
  updateCampaign: (id, data) => api.put(`/api/campaigns/${id}`, data),
  sendCampaign: (id) => api.post(`/api/campaigns/${id}/send`),
  cancelCampaign: (id) => api.post(`/api/campaigns/${id}/cancel`),
  getRecipients: (id, params) => api.get(`/api/campaigns/${id}/recipients`, { params }),
  getAnalytics: (id) => api.get(`/api/campaigns/${id}/analytics`),
  
  // Templates
  getTemplates: (params) => api.get('/api/campaigns/templates', { params }),
  createTemplate: (data) => api.post('/api/campaigns/templates', data),
  updateTemplate: (id, data) => api.put(`/api/campaigns/templates/${id}`, data),
  deleteTemplate: (id) => api.delete(`/api/campaigns/templates/${id}`),
};

// Automation API
export const automationAPI = {
  // Rules
  getRules: (params) => api.get('/api/automation/rules', { params }),
  createRule: (data) => api.post('/api/automation/rules', data),
  getRule: (id) => api.get(`/api/automation/rules/${id}`),
  updateRule: (id, data) => api.put(`/api/automation/rules/${id}`, data),
  deleteRule: (id) => api.delete(`/api/automation/rules/${id}`),
  toggleRule: (id) => api.post(`/api/automation/rules/${id}/toggle`),
  executeRule: (id) => api.post(`/api/automation/rules/${id}/execute`),
  
  // Logs
  getLogs: (params) => api.get('/api/automation/logs', { params }),
  
  // Analytics
  getAnalytics: (params) => api.get('/api/automation/analytics', { params }),
};

export default api;
