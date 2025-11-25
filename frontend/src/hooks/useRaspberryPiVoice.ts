import { useState, useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

interface Recommendation {
  id: string | number;
  name: string;
  reason: string;
}

interface UseRaspberryPiVoiceHook {
  isConnected: boolean;
  isRecording: boolean;
  transcript: string;
  recommendations: Recommendation[];
  error: string | null;
  status: string;
  connect: () => void;
  disconnect: () => void;
  startRecording: () => void;
  stopRecording: () => void;
  sendAudioChunk: (audioData: ArrayBuffer | Blob) => void;
  clearResults: () => void;
}

export const useRaspberryPiVoice = (): UseRaspberryPiVoiceHook => {
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('未连接');
  
  const socketRef = useRef<Socket | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const connect = useCallback(() => {
    if (socketRef.current?.connected) {
      return;
    }

    const socket = io('http://localhost:5000', {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });

    socket.on('connect', () => {
      console.log('已连接到服务器');
      setIsConnected(true);
      setStatus('已连接');
      setError(null);
    });

    socket.on('disconnect', () => {
      console.log('已断开连接');
      setIsConnected(false);
      setStatus('已断开');
    });

    socket.on('connected', (data: { status: string; message: string }) => {
      console.log('服务器确认连接:', data);
      setStatus(data.message);
    });

    socket.on('recording_started', (data: { status: string; message: string }) => {
      console.log('开始录音:', data);
      setIsRecording(true);
      setStatus(data.message);
      audioChunksRef.current = [];
    });

    socket.on('recording_stopped', (data: { status: string; message: string }) => {
      console.log('停止录音确认:', data);
      setIsRecording(false);
      setStatus(data.message);
    });

    socket.on('processing', (data: { status: string; message: string }) => {
      console.log('处理中:', data);
      setStatus(data.message);
    });

    socket.on('transcript', (data: { status: string; text: string; message: string }) => {
      console.log('识别结果:', data);
      setTranscript(data.text);
      setStatus(data.message);
    });

    socket.on('transcript_error', (data: { status: string; message: string }) => {
      console.error('识别错误:', data);
      setError(data.message);
      setStatus('识别失败');
      setIsRecording(false);
    });

    socket.on('recommending', (data: { status: string; message: string }) => {
      console.log('生成推荐中:', data);
      setStatus(data.message);
    });

    socket.on('recommendations', (data: { 
      status: string; 
      recommendations: Recommendation[]; 
      total_count: number;
      message: string;
    }) => {
      console.log('推荐结果:', data);
      setRecommendations(data.recommendations);
      setStatus(data.message);
    });

    socket.on('recommendation_error', (data: { status: string; message: string }) => {
      console.error('推荐错误:', data);
      setError(data.message);
      setStatus('推荐失败');
      setIsRecording(false);
    });

    socket.on('error', (data: { message: string }) => {
      console.error('错误:', data);
      setError(data.message);
      // 如果出错，确保更新录音状态
      setIsRecording(false);
    });

    socket.on('audio_received', (data: { status: string }) => {
      // 音频数据接收确认
      console.log('音频数据已接收');
    });

    socketRef.current = socket;
  }, []);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
      setIsRecording(false);
      setStatus('已断开');
    }
  }, []);

  const startRecording = useCallback(() => {
    if (!socketRef.current?.connected) {
      setError('未连接到服务器，请先连接');
      return;
    }

    socketRef.current.emit('start_recording');
    audioChunksRef.current = [];
  }, []);

  const stopRecording = useCallback(() => {
    if (!socketRef.current?.connected) {
      setError('未连接到服务器');
      return;
    }

    if (!isRecording) {
      console.log('当前未在录音状态');
      return;
    }

    console.log('发送停止录音信号');
    socketRef.current.emit('stop_recording');
    // 立即更新状态，避免等待服务器响应
    setIsRecording(false);
    setStatus('正在处理...');
  }, [isRecording]);

  const sendAudioChunk = useCallback((audioData: ArrayBuffer | Blob) => {
    if (!socketRef.current?.connected || !isRecording) {
      return;
    }

    // 将音频数据转换为base64
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64Audio = reader.result as string;
      // 移除data URL前缀
      const base64Data = base64Audio.split(',')[1];
      
      socketRef.current?.emit('audio_chunk', {
        audio: base64Data
      });
    };
    
    if (audioData instanceof Blob) {
      reader.readAsDataURL(audioData);
    } else {
      const blob = new Blob([audioData], { type: 'audio/wav' });
      reader.readAsDataURL(blob);
    }
  }, [isRecording]);

  const clearResults = useCallback(() => {
    setTranscript('');
    setRecommendations([]);
    setError(null);
    setStatus(isConnected ? '已连接' : '未连接');
  }, [isConnected]);

  // 组件卸载时断开连接
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
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
  };
};

