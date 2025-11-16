import { useState, useRef } from 'react';
import { useDishes } from '../hooks/useDishes';

const DishUploadPage = () => {
  const { analyzeDishImage, createDish, loading, error: apiError } = useDishes();
  const [image, setImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAnalysisResult(null);
      setError(null);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAnalysisResult(null);
      setError(null);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const analyzeImage = async () => {
    if (!image) return;
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const result = await analyzeDishImage(image);
      
      if (result) {
        setAnalysisResult(result);
      } else {
        setError('Failed to analyze image. Please try again.');
      }
    } catch (err) {
      setError('Failed to analyze image. Please try again.');
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!analysisResult) return;
    
    try {
      const result = await createDish(analysisResult);
      
      if (result) {
        alert('Dish successfully uploaded and saved to database!');
        // 重置表单
        setImage(null);
        setPreviewUrl(null);
        setAnalysisResult(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        setError('Failed to save dish. Please try again.');
      }
    } catch (err) {
      setError('Failed to save dish. Please try again.');
      console.error(err);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Upload New Dish</h1>
      
      <div className="bg-white rounded-lg shadow-md p-8">
        <div 
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-green-500 transition-colors"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={triggerFileInput}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleImageChange}
            accept="image/*"
            className="hidden"
          />
          
          {previewUrl ? (
            <div className="flex flex-col items-center">
              <img 
                src={previewUrl} 
                alt="Preview" 
                className="max-h-64 rounded-lg mb-4"
              />
              <p className="text-green-600 font-medium">Image selected. Click to change.</p>
            </div>
          ) : (
            <div>
              <div className="mx-auto bg-gray-200 rounded-full p-4 w-16 h-16 flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="text-gray-600 mb-2">Drag & drop an image here, or click to select</p>
              <p className="text-sm text-gray-500">Supports JPG, PNG, WEBP (Max 5MB)</p>
            </div>
          )}
        </div>
        
        {(error || apiError) && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg">
            {error || apiError}
          </div>
        )}
        
        {loading && (
          <div className="mt-4 p-4 bg-blue-50 text-blue-700 rounded-lg text-center">
            Processing...
          </div>
        )}
        
        <div className="mt-6 flex justify-center">
          <button
            onClick={analyzeImage}
            disabled={!image || isAnalyzing || loading}
            className={`px-6 py-3 rounded-lg font-medium ${
              !image || isAnalyzing || loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {isAnalyzing || loading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing...
              </span>
            ) : (
              'Analyze Dish with AI'
            )}
          </button>
        </div>
        
        {analysisResult && (
          <div className="mt-8 border-t pt-8">
            <h2 className="text-2xl font-bold mb-6">Analysis Results</h2>
            
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-gray-700 mb-2" htmlFor="name">
                    Dish Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={analysisResult.name}
                    onChange={(e) => setAnalysisResult({...analysisResult, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <div>
                  <label className="block text-gray-700 mb-2" htmlFor="price">
                    Price ($)
                  </label>
                  <input
                    type="number"
                    id="price"
                    name="price"
                    step="0.01"
                    value={analysisResult.price}
                    onChange={(e) => setAnalysisResult({...analysisResult, price: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <div className="md:col-span-2">
                  <label className="block text-gray-700 mb-2" htmlFor="description">
                    Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    value={analysisResult.description}
                    onChange={(e) => setAnalysisResult({...analysisResult, description: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <div>
                  <label className="block text-gray-700 mb-2" htmlFor="category">
                    Category
                  </label>
                  <select
                    id="category"
                    name="category"
                    value={analysisResult.category}
                    onChange={(e) => setAnalysisResult({...analysisResult, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="Appetizer">Appetizer</option>
                    <option value="Main Course">Main Course</option>
                    <option value="Dessert">Dessert</option>
                    <option value="Salad">Salad</option>
                    <option value="Soup">Soup</option>
                    <option value="Beverage">Beverage</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-gray-700 mb-2" htmlFor="spiciness">
                    Spiciness Level (0-5)
                  </label>
                  <input
                    type="range"
                    id="spiciness"
                    name="spiciness"
                    min="0"
                    max="5"
                    value={analysisResult.spiciness}
                    onChange={(e) => setAnalysisResult({...analysisResult, spiciness: parseInt(e.target.value)})}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>0</span>
                    <span>1</span>
                    <span>2</span>
                    <span>3</span>
                    <span>4</span>
                    <span>5</span>
                  </div>
                </div>
                
                <div className="md:col-span-2">
                  <label className="block text-gray-700 mb-2">
                    Ingredients
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {analysisResult.ingredients.map((ingredient: string, index: number) => (
                      <span 
                        key={index} 
                        className="bg-green-100 text-green-800 px-3 py-1 rounded-full flex items-center"
                      >
                        {ingredient}
                        <button
                          type="button"
                          onClick={() => {
                            const newIngredients = [...analysisResult.ingredients];
                            newIngredients.splice(index, 1);
                            setAnalysisResult({...analysisResult, ingredients: newIngredients});
                          }}
                          className="ml-2 text-green-600 hover:text-green-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <input
                    type="text"
                    placeholder="Add ingredient..."
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        const target = e.target as HTMLInputElement;
                        if (target.value.trim() && !analysisResult.ingredients.includes(target.value.trim())) {
                          setAnalysisResult({
                            ...analysisResult,
                            ingredients: [...analysisResult.ingredients, target.value.trim()]
                          });
                          target.value = '';
                        }
                      }
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                
                <div className="md:col-span-2">
                  <h3 className="text-lg font-medium mb-4">Nutritional Information</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <label className="block text-gray-700 mb-2" htmlFor="calories">
                        Calories
                      </label>
                      <input
                        type="number"
                        id="calories"
                        name="calories"
                        value={analysisResult.nutritionalInfo.calories}
                        onChange={(e) => setAnalysisResult({
                          ...analysisResult,
                          nutritionalInfo: {
                            ...analysisResult.nutritionalInfo,
                            calories: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-700 mb-2" htmlFor="protein">
                        Protein (g)
                      </label>
                      <input
                        type="number"
                        id="protein"
                        name="protein"
                        value={analysisResult.nutritionalInfo.protein}
                        onChange={(e) => setAnalysisResult({
                          ...analysisResult,
                          nutritionalInfo: {
                            ...analysisResult.nutritionalInfo,
                            protein: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-700 mb-2" htmlFor="carbs">
                        Carbs (g)
                      </label>
                      <input
                        type="number"
                        id="carbs"
                        name="carbs"
                        value={analysisResult.nutritionalInfo.carbs}
                        onChange={(e) => setAnalysisResult({
                          ...analysisResult,
                          nutritionalInfo: {
                            ...analysisResult.nutritionalInfo,
                            carbs: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-700 mb-2" htmlFor="fat">
                        Fat (g)
                      </label>
                      <input
                        type="number"
                        id="fat"
                        name="fat"
                        value={analysisResult.nutritionalInfo.fat}
                        onChange={(e) => setAnalysisResult({
                          ...analysisResult,
                          nutritionalInfo: {
                            ...analysisResult.nutritionalInfo,
                            fat: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end gap-4">
                <button
                  type="button"
                  onClick={() => {
                    setImage(null);
                    setPreviewUrl(null);
                    setAnalysisResult(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = '';
                    }
                  }}
                  className="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors"
                >
                  Reset
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className={`px-6 py-3 rounded-lg font-medium text-white transition-colors ${
                    loading 
                      ? 'bg-green-400 cursor-not-allowed' 
                      : 'bg-green-600 hover:bg-green-700'
                  }`}
                >
                  {loading ? 'Saving...' : 'Save to Database'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default DishUploadPage;