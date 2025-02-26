import React, { useState, useEffect } from "react";

const API_URL = "http://127.0.0.1:8000";

export default function LearningApp() {
  const [songs, setSongs] = useState([]);
  const [selectedSong, setSelectedSong] = useState(null);
  const [words, setWords] = useState([]);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/songs`)
      .then((res) => res.json())
      .then((data) => setSongs(data.songs))
      .catch((err) => console.error("Error fetching songs:", err));
  }, []);

  const selectSong = (song) => {
    setSelectedSong(song);
    fetch(`${API_URL}/song/${song}`)
      .then((res) => res.json())
      .then((data) => {
        setWords(data.words);
        setCurrentWordIndex(0);
      })
      .catch((err) => console.error("Error fetching words:", err));
  };

  const pronounceWord = () => {
    fetch(`${API_URL}/pronounce/${words[currentWordIndex]}`);
  };

  const verifyPronunciation = async () => {
    const res = await fetch(`${API_URL}/verify`, { method: "POST" });
    const data = await res.json();
    setFeedback(data.correct ? "Correct!" : `Try again! Best match: ${data.best_match}`);
    
    if (data.correct && currentWordIndex < words.length - 1) {
      setCurrentWordIndex(currentWordIndex + 1);
      setFeedback(null);
    }
  };

  return (
    <div className="p-6 text-center">
      <h1 className="text-2xl font-bold mb-4">Learning App</h1>
      {!selectedSong ? (
        <div>
          <h2 className="text-xl mb-2">Select a Song</h2>
          {songs.map((song) => (
            <button
              key={song}
              className="bg-blue-500 text-white p-2 rounded m-2"
              onClick={() => selectSong(song)}
            >
              {song}
            </button>
          ))}
        </div>
      ) : (
        <div>
          <h2 className="text-xl mb-2">{selectedSong}</h2>
          <p className="text-lg">{words[currentWordIndex]}</p>
          <button
            className="bg-green-500 text-white p-2 rounded m-2"
            onClick={pronounceWord}
          >
            Pronounce
          </button>
          <button
            className="bg-yellow-500 text-white p-2 rounded m-2"
            onClick={verifyPronunciation}
          >
            Verify
          </button>
          {feedback && <p className="mt-2 text-lg">{feedback}</p>}
        </div>
      )}
    </div>
  );
}
