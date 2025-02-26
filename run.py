from fastapi import FastAPI, HTTPException
import whisper
import pyttsx3
import os
import speech_recognition as sr
from difflib import SequenceMatcher
from typing import List, Dict, Optional

app = FastAPI()
engine = pyttsx3.init()
model = whisper.load_model("base")  # Load Whisper model
recognizer = sr.Recognizer()

# Pre-stored song list (for simplicity, using dictionary)
songs = {
    "song1": ["hello", "world"],
    "song2": ["fast", "API"]
}

# Track user progress for each song
user_progress = {}

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

@app.post("/start-song/{song_name}")
def start_song(song_name: str):
    if song_name not in songs:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Initialize or reset progress for this song
    user_progress[song_name] = {
        "current_index": 0,
        "completed": False
    }
    
    current_word = songs[song_name][0]
    
    return {
        "song": song_name,
        "current_word": current_word,
        "progress": f"Word 1 of {len(songs[song_name])}"
    }

@app.get("/current-progress/{song_name}")
def get_current_progress(song_name: str):
    if song_name not in songs:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if song_name not in user_progress:
        return {"status": "Not started", "song": song_name}
    
    progress = user_progress[song_name]
    words = songs[song_name]
    
    if progress["completed"]:
        return {"status": "Completed", "song": song_name}
    
    return {
        "status": "In progress",
        "song": song_name,
        "current_word": words[progress["current_index"]],
        "progress": f"Word {progress['current_index'] + 1} of {len(words)}"
    }

@app.post("/verify/{song_name}")
def verify_pronunciation(song_name: str):
    if song_name not in songs:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if song_name not in user_progress:
        raise HTTPException(status_code=400, detail="Please start the song first using /start-song endpoint")
    
    progress = user_progress[song_name]
    
    if progress["completed"]:
        return {"status": "Song already completed", "song": song_name}
    
    words = songs[song_name]
    current_index = progress["current_index"]
    current_word = words[current_index]
    
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
        
        similarity = similarity_ratio(current_word.lower(), recognized_text)
        is_correct = similarity >= 0.8
        
        response = {
            "recognized": recognized_text,
            "expected": current_word,
            "correct": is_correct,
            "similarity": similarity
        }
        
        # If pronunciation is correct, advance to next word
        if is_correct:
            # Check if this was the last word
            if current_index + 1 >= len(words):
                progress["completed"] = True
                response["status"] = "Song completed!"
                response["next_action"] = "Song completed. Try another song."
            else:
                # Move to next word
                progress["current_index"] += 1
                next_word = words[progress["current_index"]]
                response["next_word"] = next_word
                response["progress"] = f"Word {progress['current_index'] + 1} of {len(words)}"
                response["next_action"] = f"Proceed to pronounce: {next_word}"
        else:
            response["next_action"] = f"Try again with: {current_word}"
            
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reset/{song_name}")
def reset_progress(song_name: str):
    if song_name not in songs:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if song_name in user_progress:
        del user_progress[song_name]
    
    return {"message": f"Progress for {song_name} has been reset"}