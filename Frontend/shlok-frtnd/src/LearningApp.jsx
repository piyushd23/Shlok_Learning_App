import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, Mic, Check, X } from 'lucide-react';
import LearningApp from '../../main';

const LearningApp = () => {
  const [songs, setSongs] = useState([]);
  const [selectedSong, setSelectedSong] = useState(null);
  const [currentWord, setCurrentWord] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [message, setMessage] = useState('');
  const websocketRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Fetch available songs
    fetch('http://localhost:8000/songs')
      .then(res => res.json())
      .then(setSongs);

    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window) {
      recognitionRef.current = new webkitSpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const spokenWord = event.results[0][0].transcript.toLowerCase().trim();
        const isCorrect = spokenWord === currentWord.toLowerCase();
        
        websocketRef.current?.send(JSON.stringify({
          type: 'pronunciation_result',
          is_correct: isCorrect,
          word: spokenWord
        }));
      };
    }

    return () => {
      websocketRef.current?.close();
    };
  }, []);

  const startPractice = (songId) => {
    setSelectedSong(songId);
    
    // Close existing connection if any
    websocketRef.current?.close();
    
    // Create new WebSocket connection
    websocketRef.current = new WebSocket(`ws://localhost:8000/ws/practice/${songId}`);
    
    websocketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'word':
          setCurrentWord(data.word);
          // Play audio
          const audio = new Audio(`data:audio/mp3;base64,${data.audio}`);
          audio.onended = () => {
            // Start listening after audio plays
            setIsListening(true);
            recognitionRef.current?.start();
          };
          audio.play();
          break;
          
        case 'result':
          setMessage(data.message);
          if (!data.success) {
            // Retry after a short delay
            setTimeout(() => {
              setIsListening(true);
              recognitionRef.current?.start();
            }, 1500);
          }
          break;
          
        case 'completed':
          setMessage(data.message);
          setCurrentWord('');
          setIsListening(false);
          break;
      }
    };
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Pronunciation Practice</CardTitle>
      </CardHeader>
      <CardContent>
        {!selectedSong ? (
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Select a Song</h3>
            <div className="grid gap-2">
              {songs.map(song => (
                <Button 
                  key={song.id}
                  onClick={() => startPractice(song.id)}
                  className="w-full"
                >
                  <Play className="w-4 h-4 mr-2" />
                  {song.title}
                </Button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-6 text-center">
            <div className="text-3xl font-bold">{currentWord}</div>
            
            <div className="flex justify-center">
              {isListening ? (
                <div className="animate-pulse">
                  <Mic className="w-12 h-12 text-red-500" />
                </div>
              ) : currentWord && (
                <div className="text-gray-400">
                  <Mic className="w-12 h-12" />
                </div>
              )}
            </div>
            
            {message && (
              <div className="flex items-center justify-center gap-2">
                {message.includes('Correct') ? (
                  <Check className="w-5 h-5 text-green-500" />
                ) : message.includes('try again') ? (
                  <X className="w-5 h-5 text-red-500" />
                ) : null}
                <p>{message}</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default LearningApp;