import { useState } from 'react';
import type { User } from '../types';

const UserProfilePage = () => {
  // 模拟用户数据
  const [user, setUser] = useState<User>({
    id: 1,
    name: 'John Doe',
    email: 'john.doe@example.com',
    preferences: {
      favoriteCuisines: ['Italian', 'Japanese', 'Mediterranean'],
      dietaryRestrictions: ['Vegetarian'],
      allergens: ['Peanuts', 'Shellfish']
    },
    healthData: {
      weight: 70,
      height: 175,
      age: 30,
      activityLevel: 'moderate'
    }
  });

  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState(user);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handlePreferencesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked } = e.target;
    setFormData({
      ...formData,
      preferences: {
        ...formData.preferences,
        [name]: checked 
          ? [...(formData.preferences[name as keyof typeof formData.preferences] as string[]), value]
          : (formData.preferences[name as keyof typeof formData.preferences] as string[]).filter(item => item !== value)
      }
    });
  };

  const handleHealthDataChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      healthData: {
        ...formData.healthData,
        [name]: value
      }
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setUser(formData);
    setEditing(false);
    // 这里应该调用实际的API端点来更新用户数据
    // userService.updateUser(formData);
  };

  const activityLevels = [
    { value: 'sedentary', label: 'Sedentary (little or no exercise)' },
    { value: 'light', label: 'Light (exercise 1-3 days/week)' },
    { value: 'moderate', label: 'Moderate (exercise 3-5 days/week)' },
    { value: 'active', label: 'Active (exercise 6-7 days/week)' },
    { value: 'veryActive', label: 'Very Active (hard exercise daily)' }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">User Profile</h1>
      
      {!editing ? (
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">{user.name}</h2>
              <p className="text-gray-600">{user.email}</p>
            </div>
            <button
              onClick={() => setEditing(true)}
              className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
            >
              Edit Profile
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-bold text-gray-800 mb-4">Preferences</h3>
              <div className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2">Favorite Cuisines</h4>
                <div className="flex flex-wrap gap-2">
                  {user.preferences.favoriteCuisines.map((cuisine, index) => (
                    <span key={index} className="bg-green-100 text-green-800 px-3 py-1 rounded-full">
                      {cuisine}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2">Dietary Restrictions</h4>
                <div className="flex flex-wrap gap-2">
                  {user.preferences.dietaryRestrictions.map((restriction, index) => (
                    <span key={index} className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full">
                      {restriction}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Allergens</h4>
                <div className="flex flex-wrap gap-2">
                  {user.preferences.allergens.map((allergen, index) => (
                    <span key={index} className="bg-red-100 text-red-800 px-3 py-1 rounded-full">
                      {allergen}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-xl font-bold text-gray-800 mb-4">Health Data</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-gray-600">Age</p>
                  <p className="font-medium">{user.healthData?.age || 'Not specified'} years</p>
                </div>
                <div>
                  <p className="text-gray-600">Height</p>
                  <p className="font-medium">{user.healthData?.height || 'Not specified'} cm</p>
                </div>
                <div>
                  <p className="text-gray-600">Weight</p>
                  <p className="font-medium">{user.healthData?.weight || 'Not specified'} kg</p>
                </div>
                <div>
                  <p className="text-gray-600">Activity Level</p>
                  <p className="font-medium">
                    {activityLevels.find(level => level.value === user.healthData?.activityLevel)?.label || 'Not specified'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Edit Profile</h2>
          
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-4">Personal Information</h3>
                
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2" htmlFor="name">
                    Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2" htmlFor="email">
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <h3 className="text-xl font-bold text-gray-800 mb-4 mt-8">Preferences</h3>
                
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2">
                    Favorite Cuisines
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {['Italian', 'Japanese', 'Mediterranean', 'Mexican', 'Indian', 'Chinese'].map((cuisine) => (
                      <label key={cuisine} className="flex items-center">
                        <input
                          type="checkbox"
                          name="favoriteCuisines"
                          value={cuisine}
                          checked={formData.preferences.favoriteCuisines.includes(cuisine)}
                          onChange={handlePreferencesChange}
                          className="mr-2"
                        />
                        {cuisine}
                      </label>
                    ))}
                  </div>
                </div>
                
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2">
                    Dietary Restrictions
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {['Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 'Keto', 'Paleo'].map((restriction) => (
                      <label key={restriction} className="flex items-center">
                        <input
                          type="checkbox"
                          name="dietaryRestrictions"
                          value={restriction}
                          checked={formData.preferences.dietaryRestrictions.includes(restriction)}
                          onChange={handlePreferencesChange}
                          className="mr-2"
                        />
                        {restriction}
                      </label>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-gray-700 mb-2">
                    Allergens
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {['Peanuts', 'Tree Nuts', 'Shellfish', 'Fish', 'Eggs', 'Milk', 'Soy', 'Wheat'].map((allergen) => (
                      <label key={allergen} className="flex items-center">
                        <input
                          type="checkbox"
                          name="allergens"
                          value={allergen}
                          checked={formData.preferences.allergens.includes(allergen)}
                          onChange={handlePreferencesChange}
                          className="mr-2"
                        />
                        {allergen}
                      </label>
                    ))}
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-4">Health Data</h3>
                
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2" htmlFor="age">
                    Age
                  </label>
                  <input
                    type="number"
                    id="age"
                    name="age"
                    value={formData.healthData?.age || ''}
                    onChange={handleHealthDataChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2" htmlFor="height">
                    Height (cm)
                  </label>
                  <input
                    type="number"
                    id="height"
                    name="height"
                    value={formData.healthData?.height || ''}
                    onChange={handleHealthDataChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2" htmlFor="weight">
                    Weight (kg)
                  </label>
                  <input
                    type="number"
                    id="weight"
                    name="weight"
                    value={formData.healthData?.weight || ''}
                    onChange={handleHealthDataChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2" htmlFor="activityLevel">
                    Activity Level
                  </label>
                  <select
                    id="activityLevel"
                    name="activityLevel"
                    value={formData.healthData?.activityLevel || ''}
                    onChange={handleHealthDataChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="">Select activity level</option>
                    {activityLevels.map((level) => (
                      <option key={level.value} value={level.value}>
                        {level.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end gap-4 mt-8">
              <button
                type="button"
                onClick={() => setEditing(false)}
                className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
              >
                Save Changes
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default UserProfilePage;