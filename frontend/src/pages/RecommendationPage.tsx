import { useState, useEffect } from 'react';
import RecommendationCard from '../components/RecommendationCard';
import type { Recommendation, Dish } from '../types';

const RecommendationPage = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 模拟从API获取推荐数据
    const fetchRecommendations = async () => {
      try {
        // 这里应该调用实际的API端点
        // const response = await recommendationService.getRecommendations();
        // setRecommendations(response.data);
        
        // 模拟数据
        const mockRecommendations: Recommendation[] = [
          {
            id: 1,
            userId: 1,
            dish: {
              id: 1,
              name: 'Vegetable Stir Fry',
              description: 'Fresh vegetables stir-fried with tofu in a savory sauce',
              price: 12.99,
              category: 'Main Course',
              ingredients: ['Broccoli', 'Bell Peppers', 'Carrots', 'Tofu', 'Soy Sauce'],
              nutritionalInfo: {
                calories: 350,
                protein: 15,
                carbohydrates: 25,
                fat: 12
              },
              availability: true,
              imageUrl: '/placeholder-dish.jpg'
            } as Dish,
            reason: 'High in fiber and vitamins, aligns with your preference for plant-based meals',
            confidence: 0.92,
            timestamp: new Date().toISOString()
          },
          {
            id: 2,
            userId: 1,
            dish: {
              id: 2,
              name: 'Quinoa Salad',
              description: 'Healthy quinoa salad with mixed greens and vinaigrette',
              price: 10.99,
              category: 'Salad',
              ingredients: ['Quinoa', 'Spinach', 'Cherry Tomatoes', 'Cucumber', 'Feta Cheese'],
              nutritionalInfo: {
                calories: 280,
                protein: 10,
                carbohydrates: 30,
                fat: 8
              },
              availability: true,
              imageUrl: '/placeholder-dish.jpg'
            } as Dish,
            reason: 'Matches your dietary restrictions and provides balanced nutrition',
            confidence: 0.87,
            timestamp: new Date().toISOString()
          }
        ];
        
        setRecommendations(mockRecommendations);
        setLoading(false);
      } catch (err) {
        setError('Failed to load recommendations');
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  const handleFeedback = (recommendationId: number, feedback: 'like' | 'dislike') => {
    // 这里应该调用实际的API端点来提交反馈
    // recommendationService.submitFeedback(recommendationId, feedback);
    console.log(`Feedback for recommendation ${recommendationId}: ${feedback}`);
    
    // 更新UI以反映反馈
    setRecommendations(prev => 
      prev.map(rec => 
        rec.id === recommendationId 
          ? {...rec, feedback} 
          : rec
      )
    );
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Personalized Recommendations</h1>
        <div className="text-center py-12">
          <p>Loading recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Personalized Recommendations</h1>
        <div className="text-center py-12">
          <p className="text-red-500">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Personalized Recommendations</h1>
      <div className="mb-8 p-6 bg-blue-50 rounded-lg">
        <h2 className="text-xl font-bold mb-4">How It Works</h2>
        <p className="text-gray-700">
          Our AI analyzes your dietary preferences, health data from IoT sensors, and nutritional needs 
          to provide personalized meal recommendations. Help us improve by providing feedback on 
          each recommendation.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {recommendations.map((recommendation) => (
          <RecommendationCard 
            key={recommendation.id} 
            recommendation={recommendation} 
            onFeedback={handleFeedback}
          />
        ))}
      </div>
      
      <div className="mt-12 text-center">
        <button 
          className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-full transition duration-300"
          onClick={() => window.location.reload()}
        >
          Refresh Recommendations
        </button>
      </div>
    </div>
  );
};

export default RecommendationPage;