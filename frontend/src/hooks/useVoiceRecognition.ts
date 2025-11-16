import { useState, useRef, useCallback } from 'react';
import { voiceAPI } from '../services/api';

interface VoiceRecognitionHook {
  isRecording: boolean;
  transcript: string;
  error: string | null;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  recognizeAudio: (audioBlob: Blob) => Promise<string | null>;
  clearTranscript: () => void;
}

export const useVoiceRecognition = (): VoiceRecognitionHook => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      setError(null);
      audioChunksRef.current = [];
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await recognizeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError('无法访问麦克风，请检查权限设置');
      console.error('Error accessing microphone:', err);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const recognizeAudio = useCallback(async (audioBlob: Blob) => {
    try {
      setError(null);
      const response = await voiceAPI.recognizeSpeech(audioBlob);
      
      if (response.data.success && response.data.text) {
        setTranscript(response.data.text);
        return response.data.text;
      } else {
        setError(response.data.error || '无法识别语音内容');
        return null;
      }
    } catch (err) {
      setError('语音识别服务暂时不可用');
      console.error('Error recognizing speech:', err);
      return null;
    }
  }, []);

  const clearTranscript = useCallback(() => {
    setTranscript('');
    setError(null);
  }, []);

  return {
    isRecording,
    transcript,
    error,
    startRecording,
    stopRecording,
    recognizeAudio,
    clearTranscript
  };
};