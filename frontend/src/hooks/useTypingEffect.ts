// src/hooks/useTypingEffect.ts

import { useState, useEffect } from 'react';

export function useTypingEffect(fullText: string, speed: number = 12) {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!fullText) {
      setDisplayedText('');
      setIsComplete(false);
      return;
    }

    let index = 0;
    setDisplayedText('');
    setIsComplete(false);

    const interval = setInterval(() => {
      if (index < fullText.length) {
        setDisplayedText((prev) => prev + fullText.charAt(index));
        index++;
      } else {
        clearInterval(interval);
        setIsComplete(true);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [fullText, speed]);

  return { displayedText, isComplete };
}