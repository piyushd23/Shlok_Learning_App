from fastapi import FastAPI, HTTPException
import whisper
import pyttsx3
import os
import speech_recognition as sr
from difflib import SequenceMatcher
import json
import threading

app = FastAPI()
engine = pyttsx3.init()
model = whisper.load_model("base")
recognizer = sr.Recognizer()

songs = {
    "song1": ["hello", "how", "are", "you"],
    "song2": ["fast", "API"]
}

current_word_index = {song: 0 for song in songs}
current_song = None

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
    try:
        def speak():
            engine.say(word)
            engine.runAndWait()
        
        threading.Thread(target=speak, daemon=True).start()
        
        return {"message": f"System said '{word}'"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/verify/{song_name}")
def verify_pronunciation(song_name: str):
    global current_song, current_word_index
    
    if song_name not in songs:
        raise HTTPException(status_code=404, detail="Song not found")
    
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
        
        correct_words = songs[song_name]
        current_index = current_word_index[song_name]
        
        if current_index >= len(correct_words):
            return {"message": "Song completed"}
        
        expected_word = correct_words[current_index].lower()
        similarity = similarity_ratio(expected_word, recognized_text)
        
        if similarity >= 0.8:
            current_word_index[song_name] += 1
            return {"recognized": recognized_text, "correct": True, "similarity": similarity, "next_word": correct_words[current_word_index[song_name]] if current_word_index[song_name] < len(correct_words) else "Finished"}
        else:
            def speak():
                engine.say(expected_word)
                engine.runAndWait()
            
            threading.Thread(target=speak, daemon=True).start()
            return {"recognized": recognized_text, "correct": False, "similarity": similarity, "expected": expected_word, "message": "Repeating the word"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/next_word/{song_name}")
def get_next_word(song_name: str):
    global current_song, current_word_index
    
    if song_name not in songs:
        raise HTTPException(status_code=404, detail="Song not found")
    
    current_index = current_word_index[song_name]
    if current_index >= len(songs[song_name]):
        return {"message": "Song completed"}
    
    next_word = songs[song_name][current_index]
    return {"next_word": next_word}
