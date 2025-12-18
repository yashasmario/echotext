
import React, { useEffect } from 'react';

interface VoiceAnnouncerProps {
  message: string;
  trigger?: any;
}

export const VoiceAnnouncer: React.FC<VoiceAnnouncerProps> = ({ message, trigger }) => {
  useEffect(() => {
    if (message) {
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.rate = 0.9;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    }
  }, [message, trigger]);

  return null;
};
