import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Dish, Recommendation, User } from '../types';

// Define the store state
interface AppState {
  // User state
  user: User | null;
  isAuthenticated: boolean;
  
  // Dish state
  dishes: Dish[];
  selectedDish: Dish | null;
  
  // Recommendation state
  recommendations: Recommendation[];
  
  // UI state
  isLoading: boolean;
  error: string | null;
  
  // Actions
  // User actions
  setUser: (user: User | null) => void;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  
  // Dish actions
  setDishes: (dishes: Dish[]) => void;
  addDish: (dish: Dish) => void;
  updateDish: (dish: Dish) => void;
  removeDish: (id: number) => void;
  setSelectedDish: (dish: Dish | null) => void;
  
  // Recommendation actions
  setRecommendations: (recommendations: Recommendation[]) => void;
  addRecommendation: (recommendation: Recommendation) => void;
  updateRecommendation: (recommendation: Recommendation) => void;
  
  // UI actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

// Create the store with persistence
export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      dishes: [],
      selectedDish: null,
      recommendations: [],
      isLoading: false,
      error: null,
      
      // User actions
      setUser: (user) => set({ user }),
      setIsAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
      
      // Dish actions
      setDishes: (dishes) => set({ dishes }),
      addDish: (dish) => set((state) => ({
        dishes: [...state.dishes, dish]
      })),
      updateDish: (dish) => set((state) => ({
        dishes: state.dishes.map((d) => d.id === dish.id ? dish : d)
      })),
      removeDish: (id) => set((state) => ({
        dishes: state.dishes.filter((d) => d.id !== id)
      })),
      setSelectedDish: (selectedDish) => set({ selectedDish }),
      
      // Recommendation actions
      setRecommendations: (recommendations) => set({ recommendations }),
      addRecommendation: (recommendation) => set((state) => ({
        recommendations: [...state.recommendations, recommendation]
      })),
      updateRecommendation: (recommendation) => set((state) => ({
        recommendations: state.recommendations.map((r) => 
          r.id === recommendation.id ? recommendation : r
        )
      })),
      
      // UI actions
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null })
    }),
    {
      name: 'app-storage', // Unique name for the storage key
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated,
        dishes: state.dishes
      }), // Only persist specific parts of the state
    }
  )
);