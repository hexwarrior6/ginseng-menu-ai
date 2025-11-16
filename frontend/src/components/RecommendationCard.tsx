import type { Recommendation } from '../types';
import DishCard from './DishCard';

interface RecommendationCardProps {
  recommendation: Recommendation;
  onFeedback: (recommendationId: number, feedback: 'like' | 'dislike') => void;
}

const RecommendationCard = ({ recommendation, onFeedback }: RecommendationCardProps) => {
  const confidencePercentage = Math.round(recommendation.confidence * 100);
  
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <DishCard dish={recommendation.dish} />
      <div className="p-6 border-t border-gray-100">
        <div className="mb-4">
          <h4 className="font-bold text-gray-800 mb-2">Why we recommend this:</h4>
          <p className="text-gray-600 text-sm">{recommendation.reason}</p>
        </div>
        
        <div className="mb-4">
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm text-gray-600">Confidence</span>
            <span className="text-sm font-medium">{confidencePercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-600 h-2 rounded-full" 
              style={{ width: `${confidencePercentage}%` }}
            ></div>
          </div>
        </div>
        
        <div className="flex justify-between">
          <button
            onClick={() => onFeedback(recommendation.id, 'like')}
            className={`px-4 py-2 rounded-lg ${
              recommendation.feedback === 'like'
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            👍 Like
          </button>
          <button
            onClick={() => onFeedback(recommendation.id, 'dislike')}
            className={`px-4 py-2 rounded-lg ${
              recommendation.feedback === 'dislike'
                ? 'bg-red-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            👎 Dislike
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecommendationCard;