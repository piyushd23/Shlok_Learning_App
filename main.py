from fastapi import FastAPI, HTTPException
import whisper
import pyttsx3
import os
import speech_recognition as sr
from difflib import SequenceMatcher

app = FastAPI()
engine = pyttsx3.init()
model = whisper.load_model("base")  # Load Whisper model
recognizer = sr.Recognizer()

# Pre-stored song list (for simplicity, using dictionary)
songs = {
    "song1": ["hello", "world"],
    "song2": ["fast", "API"]
}

def similarity_ratio(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

@app.get("/songs")
def get_songs():
    return {"songs": list(songs.keys())}

@app.get("/song/{song_name}")
def get_song_words(song_name: str):
    if song_name not in songs:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"words": songs[song_name]}

@app.get("/pronounce/{word}")
def pronounce_word(word: str):
    engine.say(word)
    engine.runAndWait()
    return {"message": f"Pronounced {word}"}

@app.post("/verify")
def verify_pronunciation():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Speak now...")
            audio_data = recognizer.listen(source)
            
        with open("temp.wav", "wb") as f:
            f.write(audio_data.get_wav_data())
        
        result = model.transcribe("temp.wav")
        recognized_text = result["text"].strip().lower()
        os.remove("temp.wav")
        
        correct_words = [word.lower() for word in songs.get("song1", [])]
        best_match = max(correct_words, key=lambda w: similarity_ratio(w, recognized_text))
        similarity = similarity_ratio(best_match, recognized_text)
        
        return {"recognized": recognized_text, "correct": similarity >= 0.8, "similarity": similarity, "best_match": best_match}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
