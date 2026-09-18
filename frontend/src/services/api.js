import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token from localStorage to outgoing requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sqr_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercept 401s
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token if invalid or expired
      localStorage.removeItem('sqr_token');
      localStorage.removeItem('sqr_user');
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  testStudentRole: async () => {
    const response = await api.get('/auth/test-student');
    return response.data;
  },

  testAdminRole: async () => {
    const response = await api.get('/auth/test-admin');
    return response.data;
  },
};

export const queryService = {
  ask: async (question, category) => {
    const response = await api.post('/queries/ask', { question, category });
    return response.data;
  },

  getHistory: async () => {
    const response = await api.get('/queries/history');
    return response.data;
  },

  submitFeedback: async (queryId, rating, comment = null) => {
    const response = await api.post(`/queries/${queryId}/feedback`, { rating, comment });
    return response.data;
  },
};

export const adminKnowledgeService = {
  list: async (params = {}) => {
    const response = await api.get('/admin/knowledge', { params });
    return response.data;
  },

  create: async (itemData) => {
    const response = await api.post('/admin/knowledge', itemData);
    return response.data;
  },

  update: async (itemId, itemData) => {
    const response = await api.put(`/admin/knowledge/${itemId}`, itemData);
    return response.data;
  },

  delete: async (itemId) => {
    const response = await api.delete(`/admin/knowledge/${itemId}`);
    return response.data;
  },

  toggleStatus: async (itemId) => {
    const response = await api.patch(`/admin/knowledge/${itemId}/toggle-status`);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/admin/feedback-stats');
    return response.data;
  },
};

export const systemService = {
  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
