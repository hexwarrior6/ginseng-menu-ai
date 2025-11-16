import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';
import { voiceAPI } from '../services/api';
import VoiceTestComponent from '../components/VoiceTestComponent';

const HomePage = () => {
  const [isVoiceServiceAvailable, setIsVoiceServiceAvailable] = useState(false);
  const {
    isRecording,
    transcript,
    error,
    startRecording,
    stopRecording,
    clearTranscript
  } = useVoiceRecognition();

  // 检查语音服务是否可用
  useEffect(() => {
    const checkVoiceService = async () => {
      try {
        const response = await voiceAPI.healthCheck();
        setIsVoiceServiceAvailable(response.data.status === 'healthy');
      } catch (err) {
        setIsVoiceServiceAvailable(false);
      }
    };

    checkVoiceService();
  }, []);

  const handleVoiceInput = () => {
    if (isRecording) {
      stopRecording();
    } else {
      clearTranscript();
      startRecording();
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <section className="text-center py-12">
        <h1 className="text-4xl md:text-6xl font-bold text-green-600 mb-6">
          Welcome to Menu.ai
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Personalized dietary menu recommendations powered by IoT sensors and artificial intelligence
        </p>
        <div className="flex justify-center gap-4">
          <Link
            to="/recommendations"
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-full transition duration-300"
          >
            Get Recommendations
          </Link>
          <Link
            to="/menu"
            className="bg-white hover:bg-gray-100 text-green-600 border border-green-600 font-bold py-3 px-6 rounded-full transition duration-300"
          >
            View Menu
          </Link>
        </div>
        
        {/* 语音输入功能 */}
        {isVoiceServiceAvailable && (
          <div className="mt-12 max-w-2xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">语音点餐</h2>
              <p className="text-gray-600 mb-6">
                点击下方按钮开始语音输入，告诉我们您想吃什么
              </p>
              
              <div className="flex flex-col items-center">
                <button
                  onClick={handleVoiceInput}
                  className={`flex items-center justify-center w-16 h-16 rounded-full mb-4 transition-all duration-300 ${
                    isRecording 
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                      : 'bg-green-500 hover:bg-green-600'
                  }`}
                >
                  {isRecording ? (
                    <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1h-1V3a1 1 0 00-1-1H6zm6 6a1 1 0 10-2 0v4a1 1 0 102 0V8zm-3 5a1 1 0 10-2 0v2a1 1 0 102 0v-2zm6-4a1 1 0 10-2 0v4a1 1 0 102 0V11z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
                
                <p className="text-gray-600 mb-4">
                  {isRecording ? '正在聆听...' : '点击开始语音输入'}
                </p>
                
                {transcript && (
                  <div className="w-full mt-4">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <p className="text-gray-800">
                        <span className="font-semibold">识别结果：</span>
                        {transcript}
                      </p>
                    </div>
                  </div>
                )}
                
                {error && (
                  <div className="w-full mt-4">
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <p className="text-red-700">
                        <span className="font-semibold">错误：</span>
                        {error}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </section>

      <section className="py-12">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-green-600 text-2xl font-bold">1</span>
            </div>
            <h3 className="text-xl font-bold mb-2">IoT Sensing</h3>
            <p className="text-gray-600">
              Our IoT sensors detect your physiological state and environmental factors
            </p>
          </div>
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-green-600 text-2xl font-bold">2</span>
            </div>
            <h3 className="text-xl font-bold mb-2">AI Analysis</h3>
            <p className="text-gray-600">
              Advanced AI algorithms analyze your data to understand your dietary needs
            </p>
          </div>
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-green-600 text-2xl font-bold">3</span>
            </div>
            <h3 className="text-xl font-bold mb-2">Personalized Menu</h3>
            <p className="text-gray-600">
              Receive customized menu recommendations tailored to your unique requirements
            </p>
          </div>
        </div>
      </section>

      {/* Voice Test Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <VoiceTestComponent />
        </div>
      </section>

      <section className="py-12 bg-green-50 rounded-lg">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Transform Your Dining Experience?</h2>
          <p className="text-gray-600 mb-8 text-lg">
            Join thousands of satisfied customers who have revolutionized their eating habits with Menu.ai
          </p>
          <Link
            to="/recommendations"
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-full transition duration-300 inline-block"
          >
            Start Your Journey
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;