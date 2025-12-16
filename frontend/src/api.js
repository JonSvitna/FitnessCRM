import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export default api;
