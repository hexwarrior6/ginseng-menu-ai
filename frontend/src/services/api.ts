import axios from 'axios';
import type { Dish, NutritionalInfo } from '../types';

// 转换后端的 nutrition_info 字段名为前端的 nutritionalInfo
const transformDishFromBackend = (dish: any): Dish => {
  if (dish.nutrition_info && !dish.nutritionalInfo) {
    const { nutrition_info, ...rest } = dish;
    return {
      ...rest,
      nutritionalInfo: nutrition_info as NutritionalInfo
    };
  }
  return dish as Dish;
};

// 转换前端的 nutritionalInfo 字段名为后端的 nutrition_info
const transformDishToBackend = (dish: Partial<Dish>): any => {
  const { nutritionalInfo, ...rest } = dish;
  const transformedData: any = { ...rest };
  if (nutritionalInfo) {
    transformedData.nutrition_info = nutritionalInfo as any;
  }
  return transformedData;
};

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
});

// Request interceptor to add auth token if needed
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
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

// Auth API
export const authAPI = {
  login: (credentials: { email: string; password: string }) => 
    apiClient.post('/api/auth/login', credentials),
  register: (userData: { name: string; email: string; password: string }) => 
    apiClient.post('/api/auth/register', userData),
  logout: () => 
    apiClient.post('/api/auth/logout'),
  refreshToken: () => 
    apiClient.post('/api/auth/refresh')
};

// Dish API
export const dishAPI = {
  getAllDishes: () => 
    apiClient.get<{ dishes: any[]; total_count: number }>('/api/dishes').then(response => ({
      ...response,
      data: {
        ...response.data,
        dishes: response.data.dishes.map(transformDishFromBackend)
      }
    })),
  getDishById: (id: number) => 
    apiClient.get<any>(`/api/dishes/${id}`).then(response => ({
      ...response,
      data: transformDishFromBackend(response.data)
    })),
  createDish: (dishData: Partial<Dish>) => 
    apiClient.post<any>('/api/dishes', transformDishToBackend(dishData)).then(response => ({
      ...response,
      data: {
        ...response.data,
        dish: transformDishFromBackend(response.data.dish)
      }
    })),
  updateDish: (id: number, dishData: Partial<Dish>) => 
    apiClient.put<any>(`/api/dishes/${id}`, transformDishToBackend(dishData)).then(response => ({
      ...response,
      data: {
        ...response.data,
        dish: transformDishFromBackend(response.data.dish)
      }
    })),
  deleteDish: (id: number) => 
    apiClient.delete(`/api/dishes/${id}`),
  analyzeDishImage: (image: File) => {
    const formData = new FormData();
    formData.append('image', image);
    return apiClient.post<any>('/api/dishes/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(response => ({
      ...response,
      data: {
        ...response.data,
        dish: transformDishFromBackend(response.data.dish)
      }
    }));
  },
  analyzeMultipleDishImages: (images: File[]) => {
    const formData = new FormData();
    images.forEach((image) => {
      formData.append(`images`, image);
    });
    return apiClient.post<any>('/api/dishes/batch/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(response => ({
      ...response,
      data: {
        ...response.data,
        dishes: response.data.dishes.map(transformDishFromBackend)
      }
    }));
  },
  createMultipleDishes: (dishesData: Partial<Dish>[]) => 
    apiClient.post<any>('/api/dishes/batch', { 
      dishes: dishesData.map(transformDishToBackend) 
    }).then(response => ({
      ...response,
      data: {
        ...response.data,
        dishes: response.data.dishes.map(transformDishFromBackend)
      }
    }))
};

// Recommendation API
export const recommendationAPI = {
  getRecommendations: (preferences?: { 
    category?: string; 
    maxPrice?: number; 
    ingredients?: string[] 
  }) => apiClient.get<{ data: Dish[] }>('/api/recommendations', { params: preferences }),
  
  getSimilarDishes: (dishId: number) => 
    apiClient.get<{ data: Dish[] }>(`/api/recommendations/similar/${dishId}`)
};

// User API
export const userAPI = {
  getProfile: () => 
    apiClient.get('/api/users/profile'),
  updateProfile: (userData: Partial<{ name: string; email: string }>) => 
    apiClient.put('/api/users/profile', userData),
  changePassword: (passwords: { oldPassword: string; newPassword: string }) => 
    apiClient.put('/api/users/password', passwords)
};