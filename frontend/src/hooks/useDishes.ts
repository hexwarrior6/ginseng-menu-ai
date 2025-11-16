import { useState } from 'react';
import { useAppStore } from '../stores/useAppStore';
import { dishAPI } from '../services/api';
import type { Dish } from '../types';

export const useDishes = () => {
  const { dishes, setDishes, addDish, updateDish, removeDish, setLoading, setError } = useAppStore();
  const [loading, setLoadingState] = useState(false);
  const [error, setErrorState] = useState<string | null>(null);

  const fetchDishes = async () => {
    setLoadingState(true);
    setErrorState(null);
    setLoading(true);
    setError(null);
    
    try {
      const response = await dishAPI.getAllDishes();
      setDishes(response.data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to fetch dishes';
      setErrorState(errorMessage);
      setError(errorMessage);
      console.error('Error fetching dishes:', err);
    } finally {
      setLoadingState(false);
      setLoading(false);
    }
  };

  const fetchDishById = async (id: number) => {
    setLoadingState(true);
    setErrorState(null);
    
    try {
      const response = await dishAPI.getDishById(id);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to fetch dish';
      setErrorState(errorMessage);
      setError(errorMessage);
      console.error('Error fetching dish:', err);
      return null;
    } finally {
      setLoadingState(false);
    }
  };

  const createDish = async (dishData: Partial<Dish>) => {
    setLoadingState(true);
    setErrorState(null);
    
    try {
      const response = await dishAPI.createDish(dishData);
      addDish(response.data);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to create dish';
      setErrorState(errorMessage);
      setError(errorMessage);
      console.error('Error creating dish:', err);
      return null;
    } finally {
      setLoadingState(false);
    }
  };

  const updateDishById = async (id: number, dishData: Partial<Dish>) => {
    setLoadingState(true);
    setErrorState(null);
    
    try {
      const response = await dishAPI.updateDish(id, dishData);
      updateDish(response.data);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to update dish';
      setErrorState(errorMessage);
      setError(errorMessage);
      console.error('Error updating dish:', err);
      return null;
    } finally {
      setLoadingState(false);
    }
  };

  const deleteDishById = async (id: number) => {
    setLoadingState(true);
    setErrorState(null);
    
    try {
      await dishAPI.deleteDish(id);
      removeDish(id);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to delete dish';
      setErrorState(errorMessage);
      setError(errorMessage);
      console.error('Error deleting dish:', err);
      return false;
    } finally {
      setLoadingState(false);
    }
  };

  const analyzeDishImage = async (image: File) => {
    setLoadingState(true);
    setErrorState(null);
    
    try {
      const response = await dishAPI.analyzeDishImage(image);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to analyze dish image';
      setErrorState(errorMessage);
      setError(errorMessage);
      console.error('Error analyzing dish image:', err);
      return null;
    } finally {
      setLoadingState(false);
    }
  };

  return {
    dishes,
    loading: loading || useAppStore.getState().isLoading,
    error: error || useAppStore.getState().error,
    fetchDishes,
    fetchDishById,
    createDish,
    updateDishById,
    deleteDishById,
    analyzeDishImage
  };
};