import React, { useEffect, useRef } from 'react';
import { useRaspberryPiVoice } from '../hooks/useRaspberryPiVoice';

const VoiceTestComponent: React.FC = () => {
  const {
    isConnected,
    isRecording,
    transcript,
    recommendations,
    error,
    status,
    connect,
    disconnect,
    startRecording,
    stopRecording,
    sendAudioChunk,
    clearResults
  } = useRaspberryPiVoice();

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // 组件挂载时自动连接
  useEffect(() => {
    connect();
    return () => {
      disconnect();
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [connect, disconnect]);

  // 模拟树莓派发送音频数据（实际使用时，树莓派应该通过WebSocket发送）
  const simulateRaspberryPiAudio = () => {
    if (!isRecording) return;

    // 这里模拟从树莓派接收音频数据
    // 实际使用时，树莓派应该通过WebSocket的audio_chunk事件发送音频数据
    // 示例：创建一个空的音频Blob（实际应该是从树莓派麦克风获取的真实数据）
    const mockAudioBlob = new Blob([], { type: 'audio/wav' });
    
    // 注意：这里只是示例，实际使用时需要从树莓派获取真实的音频数据
    // 树莓派端应该使用类似以下代码发送音频：
    // socket.emit('audio_chunk', { audio: base64_encoded_audio_data })
    
    console.log('模拟发送音频数据（实际应该由树莓派发送）');
  };

  const handleToggleRecording = () => {
    if (isRecording) {
      stopRecording();
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    } else {
      clearResults();
      startRecording();
      // 模拟定时发送音频数据（实际应该由树莓派实时发送）
      // intervalRef.current = setInterval(simulateRaspberryPiAudio, 100);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">树莓派语音输入测试</h2>
      
      {/* 连接状态 */}
      <div className="mb-6 p-4 bg-gray-100 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}></span>
            <span className="font-semibold">
              状态: {status}
            </span>
          </div>
          {!isConnected && (
            <button
              onClick={connect}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg font-semibold text-white transition-colors"
            >
              重新连接
            </button>
          )}
        </div>
      </div>

      {/* 控制按钮 */}
      <div className="mb-6">
        <button
          onClick={handleToggleRecording}
          disabled={!isConnected}
          className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
            isRecording 
              ? 'bg-red-500 hover:bg-red-600' 
              : 'bg-blue-500 hover:bg-blue-600'
          } ${!isConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isRecording ? '停止录音' : '开始录音'}
        </button>
        
        <button
          onClick={clearResults}
          className="ml-4 px-6 py-3 bg-gray-500 hover:bg-gray-600 rounded-lg font-semibold text-white transition-colors"
        >
          清除结果
        </button>
      </div>

      {/* 录音状态 */}
      {isRecording && (
        <div className="mb-4 p-4 bg-yellow-100 rounded-lg">
          <p className="text-yellow-800 flex items-center">
            <span className="inline-block w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse"></span>
            正在接收树莓派音频数据...
          </p>
          <p className="text-sm text-yellow-700 mt-2">
            提示：树莓派应该通过WebSocket发送音频数据到服务器的 'audio_chunk' 事件
          </p>
          <p className="text-xs text-yellow-600 mt-1">
            如果没有树莓派，可以点击"停止录音"测试处理流程（会提示没有音频数据）
          </p>
        </div>
      )}

      {/* 识别结果 */}
      {transcript && (
        <div className="mb-4 p-4 bg-green-100 rounded-lg">
          <h3 className="font-semibold text-green-800 mb-2">语音识别结果:</h3>
          <p className="text-green-700 text-lg">{transcript}</p>
        </div>
      )}

      {/* 推荐结果 */}
      {recommendations.length > 0 && (
        <div className="mb-4 p-4 bg-blue-100 rounded-lg">
          <h3 className="font-semibold text-blue-800 mb-4">AI推荐菜品:</h3>
          <div className="space-y-3">
            {recommendations.map((rec, index) => (
              <div key={index} className="bg-white p-4 rounded-lg shadow-sm">
                <h4 className="font-bold text-lg text-gray-800 mb-1">{rec.name}</h4>
                <p className="text-gray-600">{rec.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 错误信息 */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 rounded-lg">
          <h3 className="font-semibold text-red-800">错误:</h3>
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* 使用说明 */}
      <div className="mt-8 p-4 bg-gray-100 rounded-lg">
        <h3 className="font-semibold mb-2">使用说明:</h3>
        <ul className="list-disc pl-5 text-gray-700 space-y-1">
          <li>点击"开始录音"按钮开始接收树莓派的语音数据</li>
          <li>树莓派需要通过WebSocket连接到服务器并发送音频数据</li>
          <li>树莓派发送音频数据示例代码：
            <pre className="bg-gray-200 p-2 rounded mt-2 text-xs overflow-x-auto">
{`socket.emit('audio_chunk', {
  audio: base64_encoded_audio_data
})`}
            </pre>
          </li>
          <li>说话完毕后点击"停止录音"按钮，系统将自动识别并生成推荐</li>
          <li>识别结果和推荐建议将实时显示在界面上</li>
        </ul>
      </div>
    </div>
  );
};

export default VoiceTestComponent;
