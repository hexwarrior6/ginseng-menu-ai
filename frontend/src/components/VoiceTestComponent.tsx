import React from 'react';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';

const VoiceTestComponent: React.FC = () => {
  const {
    isRecording,
    transcript,
    error,
    startRecording,
    stopRecording,
    clearTranscript
  } = useVoiceRecognition();

  const handleToggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      clearTranscript();
      startRecording();
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">语音识别测试</h2>
      
      <div className="mb-6">
        <button
          onClick={handleToggleRecording}
          className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
            isRecording 
              ? 'bg-red-500 hover:bg-red-600' 
              : 'bg-blue-500 hover:bg-blue-600'
          }`}
        >
          {isRecording ? '停止录音' : '开始录音'}
        </button>
        
        <button
          onClick={clearTranscript}
          className="ml-4 px-6 py-3 bg-gray-500 hover:bg-gray-600 rounded-lg font-semibold text-white transition-colors"
        >
          清除结果
        </button>
      </div>

      {isRecording && (
        <div className="mb-4 p-4 bg-yellow-100 rounded-lg">
          <p className="text-yellow-800">正在录音...</p>
        </div>
      )}

      {transcript && (
        <div className="mb-4 p-4 bg-green-100 rounded-lg">
          <h3 className="font-semibold text-green-800">识别结果:</h3>
          <p className="text-green-700">{transcript}</p>
        </div>
      )}

      {error && (
        <div className="mb-4 p-4 bg-red-100 rounded-lg">
          <h3 className="font-semibold text-red-800">错误:</h3>
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <div className="mt-8 p-4 bg-gray-100 rounded-lg">
        <h3 className="font-semibold mb-2">使用说明:</h3>
        <ul className="list-disc pl-5 text-gray-700">
          <li>点击"开始录音"按钮开始语音输入</li>
          <li>说话完毕后点击"停止录音"按钮</li>
          <li>系统将自动识别您的语音内容</li>
          <li>如果遇到问题，可以点击"清除结果"重新开始</li>
        </ul>
      </div>
    </div>
  );
};

export default VoiceTestComponent;