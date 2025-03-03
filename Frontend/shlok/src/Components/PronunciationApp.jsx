import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function PronunciationApp() {
  const [songs, setSongs] = useState([]);
  const [message, setMessage] = useState("");
  const [recognizedText, setRecognizedText] = useState("");
  const [bestMatch, setBestMatch] = useState("");
  const [similarity, setSimilarity] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/songs")
      .then((res) => res.json())
      .then((data) => setSongs(data.songs));
  }, []);

  const pronounceSongWords = (song) => {
    fetch(`http://127.0.0.1:8000/song/${song}`)
      .then((res) => res.json())
      .then((data) => {
        data.words.forEach((word, index) => {
          setTimeout(() => {
            fetch(`http://127.0.0.1:8000/pronounce/${word}`)
              .then((res) => res.json())
              .then((data) => setMessage(data.message));
          }, index * 2000); // Delay each word by 2 seconds
        });
      });
  };

  const verifyPronunciation = () => {
    fetch("http://127.0.0.1:8000/verify", {
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        setRecognizedText(data.recognized);
        setBestMatch(data.best_match);
        setSimilarity(data.similarity);
      });
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Pronunciation Learning App</h1>
      <h2 className="text-xl font-semibold">Songs:</h2>
      <div className="grid grid-cols-2 gap-2 my-2">
        {songs.map((song) => (
          <div key={song} className="flex justify-between items-center bg-gray-100 p-2 rounded-lg">
            <span className="text-lg">{song}</span>
            <Button onClick={() => pronounceSongWords(song)}>Play</Button>
          </div>
        ))}
      </div>
      {message && <p className="text-green-600 mt-2">{message}</p>}
      <div className="mt-4">
        <Button onClick={verifyPronunciation}>Verify Pronunciation</Button>
        {recognizedText && (
          <div className="mt-2">
            <p className="text-blue-600">Recognized: {recognizedText}</p>
            <p className="text-green-600">Best Match: {bestMatch}</p>
            <p className="text-gray-600">Similarity: {similarity}</p>
          </div>
        )}
      </div>
    </div>
  );
}
