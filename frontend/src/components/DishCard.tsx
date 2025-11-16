import type { Dish } from '../types';

interface DishCardProps {
  dish: Dish;
}

const DishCard = ({ dish }: DishCardProps) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      {dish.imageUrl ? (
        <img 
          src={dish.imageUrl} 
          alt={dish.name} 
          className="w-full h-48 object-cover"
        />
      ) : (
        <div className="bg-gray-200 border-2 border-dashed rounded-xl w-full h-48 flex items-center justify-center">
          <span className="text-gray-500">No Image</span>
        </div>
      )}
      <div className="p-6">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-xl font-bold text-gray-800">{dish.name}</h3>
          <span className="text-lg font-semibold text-green-600">${dish.price.toFixed(2)}</span>
        </div>
        <p className="text-gray-600 mb-4">{dish.description}</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {dish.ingredients.slice(0, 3).map((ingredient, index) => (
            <span 
              key={index} 
              className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full"
            >
              {ingredient}
            </span>
          ))}
          {dish.ingredients.length > 3 && (
            <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">
              +{dish.ingredients.length - 3} more
            </span>
          )}
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500">{dish.category}</span>
          <div className="flex items-center">
            <span className="text-sm text-gray-500 mr-2">Cal:</span>
            <span className="font-medium">{dish.nutritionalInfo.calories}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DishCard;