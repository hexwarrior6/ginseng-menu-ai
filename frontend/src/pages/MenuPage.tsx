import { useState, useEffect } from 'react';
import DishCard from '../components/DishCard';
import type { Dish } from '../types';

const MenuPage = () => {
  const [dishes, setDishes] = useState<Dish[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 模拟从API获取菜品数据
    const fetchDishes = async () => {
      try {
        // 这里应该调用实际的API端点
        // const response = await dishService.getAllDishes();
        // setDishes(response.data);
        
        // 模拟数据
        const mockDishes: Dish[] = [
          {
            id: 1,
            name: 'Vegetable Stir Fry',
            description: 'Fresh vegetables stir-fried with tofu in a savory sauce',
            price: 12.99,
            category: 'Main Course',
            ingredients: ['Broccoli', 'Bell Peppers', 'Carrots', 'Tofu', 'Soy Sauce'],
            nutritionalInfo: {
              calories: 350,
              protein: 15,
              carbs: 25,
              fat: 12
            },
            availability: true,
            imageUrl: '/placeholder-dish.jpg'
          },
          {
            id: 2,
            name: 'Quinoa Salad',
            description: 'Healthy quinoa salad with mixed greens and vinaigrette',
            price: 10.99,
            category: 'Salad',
            ingredients: ['Quinoa', 'Spinach', 'Cherry Tomatoes', 'Cucumber', 'Feta Cheese'],
            nutritionalInfo: {
              calories: 280,
              protein: 10,
              carbs: 30,
              fat: 8
            },
            availability: true,
            imageUrl: '/placeholder-dish.jpg'
          }
        ];
        
        setDishes(mockDishes);
        setLoading(false);
      } catch (err) {
        setError('Failed to load dishes');
        setLoading(false);
      }
    };

    fetchDishes();
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Our Menu</h1>
        <div className="text-center py-12">
          <p>Loading dishes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Our Menu</h1>
        <div className="text-center py-12">
          <p className="text-red-500">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Our Menu</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {dishes.map((dish) => (
          <DishCard key={dish.id} dish={dish} />
        ))}
      </div>
    </div>
  );
};

export default MenuPage;