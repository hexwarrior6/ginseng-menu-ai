import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { Dish } from '../types';

const DishDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [dish, setDish] = useState<Dish | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 模拟从API获取菜品详情
    const fetchDish = async () => {
      try {
        // 这里应该调用实际的API端点
        // const response = await dishService.getDishById(id);
        // setDish(response.data);
        
        // 模拟数据
        const mockDish: Dish = {
          id: parseInt(id || '1'),
          name: 'Vegetable Stir Fry',
          description: 'Fresh vegetables stir-fried with tofu in a savory sauce',
          price: 12.99,
          category: 'Main Course',
          ingredients: ['Broccoli', 'Bell Peppers', 'Carrots', 'Tofu', 'Soy Sauce', 'Garlic', 'Ginger'],
          nutritionalInfo: {
            calories: 350,
            protein: 15,
            carbs: 25,
            fat: 12
          },
          availability: true,
          imageUrl: '/placeholder-dish.jpg',
          spiciness: 2
        };
        
        setDish(mockDish);
        setLoading(false);
      } catch (err) {
        setError('Failed to load dish details');
        setLoading(false);
      }
    };

    if (id) {
      fetchDish();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <p>Loading dish details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <p className="text-red-500">{error}</p>
        </div>
      </div>
    );
  }

  if (!dish) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <p>Dish not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Link to="/menu" className="text-green-600 hover:text-green-800 mb-4 inline-block">
        ← Back to Menu
      </Link>
      
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="md:flex">
          <div className="md:w-1/2">
            {dish.imageUrl ? (
              <img 
                src={dish.imageUrl} 
                alt={dish.name} 
                className="w-full h-96 object-cover"
              />
            ) : (
              <div className="bg-gray-200 border-2 border-dashed rounded-xl w-full h-96 flex items-center justify-center">
                <span className="text-gray-500">No Image</span>
              </div>
            )}
          </div>
          
          <div className="md:w-1/2 p-8">
            <div className="flex justify-between items-start mb-4">
              <h1 className="text-3xl font-bold text-gray-800">{dish.name}</h1>
              <span className="text-2xl font-bold text-green-600">${dish.price.toFixed(2)}</span>
            </div>
            
            <p className="text-gray-600 mb-6">{dish.description}</p>
            
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-800 mb-2">Ingredients</h2>
              <div className="flex flex-wrap gap-2">
                {dish.ingredients.map((ingredient, index) => (
                  <span 
                    key={index} 
                    className="bg-green-100 text-green-800 px-3 py-1 rounded-full"
                  >
                    {ingredient}
                  </span>
                ))}
              </div>
            </div>
            
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-800 mb-2">Nutritional Information</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-600">Calories</p>
                  <p className="text-2xl font-bold">{dish.nutritionalInfo.calories}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-600">Protein</p>
                  <p className="text-2xl font-bold">{dish.nutritionalInfo.protein}g</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-600">Carbs</p>
                  <p className="text-2xl font-bold">{dish.nutritionalInfo.carbs}g</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-600">Fat</p>
                  <p className="text-2xl font-bold">{dish.nutritionalInfo.fat}g</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center mb-6">
              <span className="text-gray-600 mr-2">Spiciness:</span>
              <div className="flex">
                {[...Array(5)].map((_, i) => (
                  <span 
                    key={i} 
                    className={`text-xl ${i < (dish.spiciness || 0) ? 'text-red-500' : 'text-gray-300'}`}
                  >
                    ●
                  </span>
                ))}
              </div>
            </div>
            
            <div className="flex gap-4">
              <button className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300 flex-1">
                Add to Order
              </button>
              <button className="bg-white hover:bg-gray-100 text-green-600 border border-green-600 font-bold py-3 px-6 rounded-lg transition duration-300">
                Favorite
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DishDetailPage;