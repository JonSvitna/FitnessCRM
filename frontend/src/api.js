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
  getAll: () => api.get('/api/trainers'),
  getById: (id) => api.get(`/api/trainers/${id}`),
  update: (id, data) => api.put(`/api/trainers/${id}`, data),
  delete: (id) => api.delete(`/api/trainers/${id}`),
};

// Client API
export const clientAPI = {
  create: (data) => api.post('/api/clients', data),
  getAll: () => api.get('/api/clients'),
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

export default api;
