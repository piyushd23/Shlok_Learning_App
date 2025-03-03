from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import threading
import pyttsx3
import requests
from typing import List, Dict, Optional

app = FastAPI()

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Sample song lyrics storage
songs = {
    "twinkle": ["Twinkle", "twinkle", "little", "star", "how", "I", "wonder", "what", "you", "are"],
    "abc": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"],
    "row_boat": ["Row", "row", "row", "your", "boat", "gently", "down", "the", "stream"]
}

# Track current song and word position for each session
sessions = {}

class SessionData(BaseModel):
    song_id: str
    current_position: int = 0
    completed: bool = False

class VerificationResult(BaseModel):
    is_correct: bool
    message: Optional[str] = None

@app.post("/start_song/{song_id}")
def start_song(song_id: str):
    if song_id not in songs:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Create a new session
    session_id = f"session_{len(sessions) + 1}"
    sessions[session_id] = SessionData(song_id=song_id)
    
    # Get the first word
    first_word = songs[song_id][0]
    
    # Return session info and first word
    return {
        "session_id": session_id,
        "song_id": song_id,
        "current_word": first_word,
        "position": 0,
        "total_words": len(songs[song_id])
    }

@app.get("/pronounce/{session_id}")
def pronounce_word(session_id: str):
    # Check if session exists
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Check if song is completed
    if session.completed:
        return {"message": "Song completed", "completed": True}
    
    # Get the current word
    song_lyrics = songs[session.song_id]
    current_word = song_lyrics[session.current_position]
    
    # Create JSON representation and print to console
    word_data = {"word": current_word}
    json_data = json.dumps(word_data)
    print(json_data)
    
    # Pronounce word in a separate thread
    def speak():
        engine.say(current_word)
        engine.runAndWait()
    
    threading.Thread(target=speak, daemon=True).start()
    
    return {
        "message": f"Pronouncing word: {current_word}",
        "current_word": current_word,
        "position": session.current_position,
        "total_words": len(song_lyrics),
        "session_id": session_id
    }

@app.post("/verify/{session_id}")
def verify_pronunciation(session_id: str, result: VerificationResult):
    # Check if session exists
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Check if song is already completed
    if session.completed:
        return {"message": "Song already completed", "completed": True}
    
    # Get the song lyrics
    song_lyrics = songs[session.song_id]
    current_word = song_lyrics[session.current_position]
    
    if result.is_correct:
        # Move to the next word
        session.current_position += 1
        
        # Check if we've reached the end of the song
        if session.current_position >= len(song_lyrics):
            session.completed = True
            return {
                "message": "Pronunciation correct. Song completed!",
                "completed": True,
                "next_word": None
            }
        
        # Get the next word
        next_word = song_lyrics[session.current_position]
        
        return {
            "message": f"Pronunciation correct. Moving to next word: {next_word}",
            "completed": False,
            "next_word": next_word,
            "position": session.current_position,
            "total_words": len(song_lyrics)
        }
    else:
        # If verification failed, stay on the same word
        return {
            "message": "Pronunciation incorrect. Please try again.",
            "completed": False,
            "next_word": current_word,  # Stay on the same word
            "position": session.current_position,
            "total_words": len(song_lyrics)
        }

@app.get("/song_progress/{session_id}")
def get_progress(session_id: str):
    # Check if session exists
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    song_lyrics = songs[session.song_id]
    
    return {
        "session_id": session_id,
        "song_id": session.song_id,
        "current_position": session.current_position,
        "total_words": len(song_lyrics),
        "completed": session.completed,
        "current_word": song_lyrics[session.current_position] if not session.completed else None,
        "progress_percentage": round((session.current_position / len(song_lyrics)) * 100, 2)
    }

@app.get("/available_songs")
def list_songs():
    return {
        "available_songs": [
            {"id": song_id, "words": len(words)} 
            for song_id, words in songs.items()
        ]
    }