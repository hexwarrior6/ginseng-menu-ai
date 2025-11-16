export interface NutritionalInfo {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

export interface Dish {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  ingredients: string[];
  nutritionalInfo: NutritionalInfo;
  availability: boolean;
  imageUrl?: string;
  spiciness?: number; // 辣度 (0-5)
}

export interface Recommendation {
  id: number;
  userId: number;
  dish: Dish;
  reason: string;
  confidence: number;
  timestamp: string;
  feedback?: 'like' | 'dislike';
}

export interface User {
  id: number;
  name: string;
  email: string;
  preferences: {
    favoriteCuisines: string[];
    dietaryRestrictions: string[];
    allergens: string[];
  };
  healthData?: {
    weight?: number;
    height?: number;
    age?: number;
    activityLevel?: 'sedentary' | 'light' | 'moderate' | 'active' | 'veryActive';
  };
}