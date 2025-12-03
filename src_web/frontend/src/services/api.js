// api.js - API service for the canteen admin panel
import axios from 'axios';

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000', // Update this to match your backend URL
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth tokens if needed
apiClient.interceptors.request.use(
  (config) => {
    // You can add authentication headers here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors globally
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    // Handle global error cases here if needed
    return Promise.reject(error);
  }
);

export default apiClient;

// API endpoints
export const userApi = {
  getAll: () => apiClient.get('/users'),
  getById: (id) => apiClient.get(`/users/${id}`),
};

export const dishApi = {
  getAll: () => apiClient.get('/dishes'),
  getById: (id) => apiClient.get(`/dishes/${id}`),
  create: (data) => apiClient.post('/dishes', data),
  update: (id, data) => apiClient.patch(`/dishes/${id}`, data),
  delete: (id) => apiClient.delete(`/dishes/${id}`),
};

export const userDishApi = {
  getAll: () => apiClient.get('/user-dishes'),
  getByUid: (uid) => apiClient.get(`/user-dishes/uid/${uid}`),
  getById: (id) => apiClient.get(`/user-dishes/${id}`),
  create: (data) => apiClient.post('/user-dishes', data),
  delete: (id) => apiClient.delete(`/user-dishes/${id}`),
  deleteByUidAndDishName: (uid, dishName) => apiClient.delete(`/user-dishes/uid/${uid}/dish/${dishName}`),
};

export const logApi = {
  getAll: () => apiClient.get('/interaction-logs'),
  getById: (id) => apiClient.get(`/interaction-logs/${id}`),
  getByUserId: (userId) => apiClient.get(`/interaction-logs/user/${userId}`),
  delete: (id) => apiClient.delete(`/interaction-logs/${id}`),
};

export const dataInsightApi = {
  getStats: () => apiClient.get('/data-insight/dashboard-stats'),
  getUserPreferences: (userId) => apiClient.get(`/data-insight/user-preferences/${userId}`),
  getPopularDishes: (limit = 10, timeRange = 'history', startDate = null, endDate = null) => {
    let url = `/data-insight/popular-dishes?limit=${limit}&timeRange=${timeRange}`;
    if (startDate) url += `&startDate=${startDate}`;
    if (endDate) url += `&endDate=${endDate}`;
    return apiClient.get(url);
  },
  getRecentActivity: (limit = 12) => apiClient.get(`/data-insight/recent-activity?limit=${limit}`),
  getAiAnalysis: () => apiClient.get('/data-insight/ai-analysis', { timeout: 120000 }),
};