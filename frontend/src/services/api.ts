import axios from 'axios';
import type { Dish, Recommendation, User } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (email: string, password: string) => 
    apiClient.post('/auth/login', { email, password }),
  
  register: (userData: Partial<User>) => 
    apiClient.post('/auth/register', userData),
  
  logout: () => {
    localStorage.removeItem('authToken');
    return Promise.resolve();
  }
};

// Dish APIs
export const dishAPI = {
  getAllDishes: () => 
    apiClient.get<Dish[]>('/dishes'),
  
  getDishById: (id: number) => 
    apiClient.get<Dish>(`/dishes/${id}`),
  
  createDish: (dishData: Partial<Dish>) => 
    apiClient.post<Dish>('/dishes', dishData),
  
  updateDish: (id: number, dishData: Partial<Dish>) => 
    apiClient.put<Dish>(`/dishes/${id}`, dishData),
  
  deleteDish: (id: number) => 
    apiClient.delete(`/dishes/${id}`),
  
  analyzeDishImage: (image: File) => {
    const formData = new FormData();
    formData.append('image', image);
    return apiClient.post('/dishes/analyze-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
};

// Recommendation APIs
export const recommendationAPI = {
  getRecommendations: (userId: number) => 
    apiClient.get<Recommendation[]>(`/recommendations?userId=${userId}`),
  
  getRecommendationById: (id: number) => 
    apiClient.get<Recommendation>(`/recommendations/${id}`),
  
  createRecommendation: (recommendationData: Partial<Recommendation>) => 
    apiClient.post<Recommendation>('/recommendations', recommendationData),
  
  updateRecommendationFeedback: (id: number, feedback: { liked: boolean }) => 
    apiClient.patch<Recommendation>(`/recommendations/${id}/feedback`, feedback)
};

// User APIs
export const userAPI = {
  getUserProfile: () => 
    apiClient.get<User>('/users/profile'),
  
  updateUserProfile: (userData: Partial<User>) => 
    apiClient.put<User>('/users/profile', userData),
  
  deleteUserAccount: () => 
    apiClient.delete('/users/profile')
};

// Export the base client for any custom requests
export default apiClient;