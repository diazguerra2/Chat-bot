import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (message, sessionId = null) => {
    const response = await api.post('/chat/', {
      message,
      sessionId,
    });
    return response.data;
  },
  
  getChatHistory: async () => {
    const response = await api.get('/chat/history');
    return response.data;
  },
};

// Certifications API
export const certificationsAPI = {
  getAll: async () => {
    const response = await api.get('/certifications');
    return response.data;
  },
  
  getById: async (certId) => {
    const response = await api.get(`/certifications/${certId}`);
    return response.data;
  },
  
  getRequirements: async (certId) => {
    const response = await api.get(`/certifications/${certId}/requirements`);
    return response.data;
  },
  
  getRecommendations: async (params) => {
    const response = await api.get('/certifications/recommendations', { params });
    return response.data;
  },
  
  getTrainingProviders: async (params) => {
    const response = await api.get('/certifications/training-providers', { params });
    return response.data;
  },
  
  getCourses: async (certId) => {
    const response = await api.get(`/certifications/${certId}/courses`);
    return response.data;
  },
};

// Advice API
export const adviceAPI = {
  getExperienceBased: async (data) => {
    const response = await api.post('/advice/experience-based', data);
    return response.data;
  },
  
  getCareerMatch: async (data) => {
    const response = await api.post('/advice/career-match', data);
    return response.data;
  },
};

export default api;
