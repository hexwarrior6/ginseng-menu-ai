import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useDishes } from '../hooks/useDishes';
import { X, Upload, Sparkles, Plus, Trash2 } from 'lucide-react';
import type { Dish } from '../types';



const DishUploadPage: React.FC = () => {
  const { analyzeDishImage, createDish, analyzeMultipleDishImages, createMultipleDishes, loading, error } = useDishes();
  
  // Single upload states
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  
  // Batch upload states
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [batchPreviewUrls, setBatchPreviewUrls] = useState<string[]>([]);
  const [isBatchAnalyzing, setIsBatchAnalyzing] = useState(false);
  const [batchAnalysisResults, setBatchAnalysisResults] = useState<any[]>([]);
  
  // Form states
  const [dishData, setDishData] = useState<Partial<Dish>>({
    name: '',
    price: 0,
    description: '',
    category: '',
    spiciness: 0,
    ingredients: [],
    nutritionalInfo: {
      calories: 0,
      protein: 0,
      carbohydrates: 0,
      fat: 0
    }
  });
  
  const [batchDishData, setBatchDishData] = useState<Partial<Dish>[]>([]);
  
  const onDropSingle = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAnalysisResult(null);
    }
  }, []);

  const onDropMultiple = useCallback((acceptedFiles: File[]) => {
    const newImages = [...selectedImages, ...acceptedFiles];
    setSelectedImages(newImages);
    
    const newPreviewUrls = [
      ...batchPreviewUrls,
      ...acceptedFiles.map(file => URL.createObjectURL(file))
    ];
    setBatchPreviewUrls(newPreviewUrls);
    
    // Initialize empty analysis results for new images
    const newResults = [
      ...batchAnalysisResults,
      ...acceptedFiles.map(() => null)
    ];
    setBatchAnalysisResults(newResults);
  }, [selectedImages, batchPreviewUrls, batchAnalysisResults]);

  const { getRootProps: getSingleRootProps, getInputProps: getSingleInputProps } = useDropzone({
    onDrop: onDropSingle,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 1
  });

  const { getRootProps: getBatchRootProps, getInputProps: getBatchInputProps } = useDropzone({
    onDrop: onDropMultiple,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 10
  });

  const removeImage = (index: number) => {
    const newImages = [...selectedImages];
    newImages.splice(index, 1);
    setSelectedImages(newImages);
    
    const newPreviewUrls = [...batchPreviewUrls];
    newPreviewUrls.splice(index, 1);
    setBatchPreviewUrls(newPreviewUrls);
    
    const newResults = [...batchAnalysisResults];
    newResults.splice(index, 1);
    setBatchAnalysisResults(newResults);
  };

  const analyzeImage = async () => {
    if (!selectedImage) return;
    
    setIsAnalyzing(true);
    try {
      const result = await analyzeDishImage(selectedImage);
      if (result) {
        setAnalysisResult(result);
        setDishData({
          name: result.name || '',
          price: result.price || 0,
          description: result.description || '',
          category: result.category || '',
          spiciness: result.spiciness || 0,
          ingredients: result.ingredients || [],
          nutritionalInfo: result.nutritionalInfo || {
            calories: 0,
            protein: 0,
            carbohydrates: 0,
            fat: 0
          }
        });
      }
    } catch (err) {
      console.error('Analysis failed:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const analyzeBatchImages = async () => {
    if (selectedImages.length === 0) return;
    
    setIsBatchAnalyzing(true);
    try {
      const results = await analyzeMultipleDishImages(selectedImages);
      if (results && Array.isArray(results)) {
        setBatchAnalysisResults(results);
        setBatchDishData(results);
      }
    } catch (err) {
      console.error('Batch analysis failed:', err);
    } finally {
      setIsBatchAnalyzing(false);
    }
  };

  const handleInputChange = (field: keyof Dish, value: any) => {
    setDishData(prev => ({ ...prev, [field]: value }));
  };

  const handleNutritionChange = (field: string, value: number) => {
    setDishData(prev => ({
      ...prev,
      nutritionalInfo: {
        calories: 0,
        protein: 0,
        carbohydrates: 0,
        fat: 0,
        ...(prev.nutritionalInfo || {}),
        [field]: value
      }
    }));
  };

  // Removed unused functions since ingredients is string[] in Dish type

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createDish(dishData);
  };

  const handleBatchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createMultipleDishes(batchDishData);
  };

  const resetForm = () => {
    setSelectedImage(null);
    setPreviewUrl(null);
    setAnalysisResult(null);
    setDishData({
      name: '',
      price: 0,
      description: '',
      category: '',
      spiciness: 0,
      ingredients: [],
      nutritionalInfo: {
            calories: 0,
            protein: 0,
            carbohydrates: 0,
            fat: 0
          }
    });
  };

  const resetBatchForm = () => {
    setSelectedImages([]);
    setBatchPreviewUrls([]);
    setBatchAnalysisResults([]);
    setBatchDishData([]);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">菜品上传</h1>
      
      {/* Tabs for Single vs Batch Upload */}
      <div className="mb-8 border-b border-gray-200">
        <nav className="flex space-x-8">
          <button className="py-4 px-1 border-b-2 border-blue-500 text-blue-600 font-medium text-sm">
            单个菜品上传
          </button>
          <button className="py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 font-medium text-sm">
            批量菜品上传
          </button>
        </nav>
      </div>
      
      {/* Single Upload Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">上传菜品图片</h2>
        
        {/* Image Upload Area */}
        <div 
          {...getSingleRootProps()} 
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
        >
          <input {...getSingleInputProps()} />
          {previewUrl ? (
            <div className="relative inline-block">
              <img src={previewUrl} alt="Preview" className="max-h-64 rounded-lg" />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedImage(null);
                  setPreviewUrl(null);
                  setAnalysisResult(null);
                }}
                className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
              >
                <X size={16} />
              </button>
            </div>
          ) : (
            <div>
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-600">
                拖拽图片到这里，或点击选择图片
              </p>
              <p className="text-xs text-gray-500">
                支持 JPG、PNG 格式
              </p>
            </div>
          )}
        </div>
        
        {/* Analyze Button */}
        {selectedImage && !analysisResult && (
          <div className="mt-4">
            <button
              onClick={analyzeImage}
              disabled={isAnalyzing}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <Sparkles size={16} />
              {isAnalyzing ? 'AI 分析中...' : '使用 AI 分析菜品'}
            </button>
          </div>
        )}
        
        {/* Analysis Result */}
        {analysisResult && (
          <div className="mt-6 p-4 bg-green-50 rounded-lg">
            <h3 className="font-medium text-green-800">AI 分析完成！</h3>
            <p className="text-sm text-green-700 mt-1">
              已自动填充菜品信息，请核对并完善后保存。
            </p>
          </div>
        )}
        
        {/* Dish Form */}
        <form onSubmit={handleSubmit} className="mt-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              菜品名称 *
            </label>
            <input
              type="text"
              value={dishData.name || ''}
              onChange={(e) => handleInputChange('name', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                价格 *
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={dishData.price || 0}
                onChange={(e) => handleInputChange('price', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                分类
              </label>
              <select
                value={dishData.category || ''}
                onChange={(e) => handleInputChange('category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">请选择分类</option>
                <option value="主菜">主菜</option>
                <option value="汤类">汤类</option>
                <option value="小食">小食</option>
                <option value="饮品">饮品</option>
                <option value="甜品">甜品</option>
              </select>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              描述
            </label>
            <textarea
              value={dishData.description || ''}
              onChange={(e) => handleInputChange('description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              辣度 (0-5)
            </label>
            <div className="flex items-center gap-4">
              <input
              type="range"
              min="0"
              max="5"
              value={dishData.spiciness || 0}
              onChange={(e) => handleInputChange('spiciness', parseInt(e.target.value))}
              className="w-full"
            />
            <span className="text-sm font-medium text-gray-700 w-8">
              {dishData.spiciness || 0}
            </span>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700">
                食材
              </label>
              <button
                type="button"
                onClick={() => {
                  const newIngredients = [...(dishData.ingredients || []), ''];
                  handleInputChange('ingredients', newIngredients);
                }}
                className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
              >
                <Plus size={16} />
                添加食材
              </button>
            </div>
            
            <div className="space-y-2">
              {/* Since ingredients is string[] in Dish type, we display it as a simple list */}
              {(dishData.ingredients || []).map((ingredient, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="text"
                    placeholder="食材"
                    value={ingredient}
                    onChange={(e) => {
                      const newIngredients = [...(dishData.ingredients || [])];
                      newIngredients[index] = e.target.value;
                      handleInputChange('ingredients', newIngredients);
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      const newIngredients = [...(dishData.ingredients || [])];
                      newIngredients.splice(index, 1);
                      handleInputChange('ingredients', newIngredients);
                    }}
                    className="p-2 text-red-600 hover:text-red-800"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={() => {
                  const newIngredients = [...(dishData.ingredients || []), ''];
                  handleInputChange('ingredients', newIngredients);
                }}
                className="flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm"
              >
                <Plus size={14} />
                添加食材
              </button>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              营养信息
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">热量 (kcal)</label>
                <input
                  type="number"
                  min="0"
                  value={dishData.nutritionalInfo?.calories || 0}
                  onChange={(e) => handleNutritionChange('calories', parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">蛋白质 (g)</label>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={dishData.nutritionalInfo?.protein || 0}
                  onChange={(e) => handleNutritionChange('protein', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">碳水 (g)</label>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={dishData.nutritionalInfo?.carbohydrates || 0}
                onChange={(e) => handleNutritionChange('carbohydrates', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">脂肪 (g)</label>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={dishData.nutritionalInfo?.fat || 0}
                  onChange={(e) => handleNutritionChange('fat', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
          
          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? '保存中...' : '保存到数据库'}
            </button>
            <button
              type="button"
              onClick={resetForm}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              重置
            </button>
          </div>
          
          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md">
              {error}
            </div>
          )}
        </form>
      </div>
      
      {/* Batch Upload Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">批量上传菜品图片</h2>
        
        {/* Batch Image Upload Area */}
        <div 
          {...getBatchRootProps()} 
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
        >
          <input {...getBatchInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            拖拽多张图片到这里，或点击选择图片
          </p>
          <p className="text-xs text-gray-500">
            支持 JPG、PNG 格式，最多可同时上传 10 张图片
          </p>
        </div>
        
        {/* Selected Images Preview */}
        {selectedImages.length > 0 && (
          <div className="mt-6">
            <h3 className="text-lg font-medium text-gray-800 mb-3">已选择 {selectedImages.length} 张图片</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {batchPreviewUrls.map((url, index) => (
                <div key={index} className="relative group">
                  <img 
                    src={url} 
                    alt={`Preview ${index}`} 
                    className="w-full h-32 object-cover rounded-lg border border-gray-200"
                  />
                  <button
                    onClick={() => removeImage(index)}
                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X size={14} />
                  </button>
                  {batchAnalysisResults[index] && (
                    <div className="absolute bottom-1 left-1 right-1 bg-green-500 text-white text-xs text-center py-1 rounded-b-lg">
                      已分析
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            {/* Batch Analyze Button */}
            <div className="mt-4">
              <button
                onClick={analyzeBatchImages}
                disabled={isBatchAnalyzing || selectedImages.length === 0}
                className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                <Sparkles size={16} />
                {isBatchAnalyzing ? 'AI 批量分析中...' : '使用 AI 批量分析菜品'}
              </button>
            </div>
            
            {/* Batch Analysis Results */}
            {batchAnalysisResults.length > 0 && (
              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <h3 className="font-medium text-green-800">AI 批量分析完成！</h3>
                <p className="text-sm text-green-700 mt-1">
                  已自动识别 {batchAnalysisResults.filter(r => r !== null).length} 个菜品信息。
                </p>
                
                {/* Batch Dish Forms */}
                <div className="mt-4 space-y-6">
                  {batchAnalysisResults.map((result, index) => result && (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-800 mb-2">菜品 {index + 1}</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            菜品名称
                          </label>
                          <input
                            type="text"
                            value={result.name || ''}
                            onChange={(e) => {
                              const newResults = [...batchAnalysisResults];
                              newResults[index] = { ...newResults[index], name: e.target.value };
                              setBatchAnalysisResults(newResults);
                              
                              const newData = [...batchDishData];
                              newData[index] = { ...newData[index], name: e.target.value };
                              setBatchDishData(newData);
                            }}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            价格
                          </label>
                          <input
                            type="number"
                            min="0"
                            step="0.01"
                            value={result.price || 0}
                            onChange={(e) => {
                              const newResults = [...batchAnalysisResults];
                              newResults[index] = { ...newResults[index], price: parseFloat(e.target.value) || 0 };
                              setBatchAnalysisResults(newResults);
                              
                              const newData = [...batchDishData];
                              newData[index] = { ...newData[index], price: parseFloat(e.target.value) || 0 };
                              setBatchDishData(newData);
                            }}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Batch Submit Button */}
                <div className="mt-6">
                  <button
                    onClick={handleBatchSubmit}
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading ? '批量保存中...' : '批量保存到数据库'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Batch Reset Button */}
        {selectedImages.length > 0 && (
          <div className="mt-4">
            <button
              onClick={resetBatchForm}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              清空所有
            </button>
          </div>
        )}
        
        {error && (
          <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default DishUploadPage;