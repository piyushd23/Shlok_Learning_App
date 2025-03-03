from fastapi import FastAPI, HTTPException
import whisper
import pyttsx3
import os
import speech_recognition as sr
from difflib import SequenceMatcher
import json
import threading

def similarity_ratio(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

app = FastAPI()
engine = pyttsx3.init()
model = whisper.load_model("base")
recognizer = sr.Recognizer()

songs = {
    "song1": ["hello","apple","orange"],
    "song2": ["hello", "apple"],
    "twinkle": ["Twinkle", "twinkle", "little", "star", "how", "I", "wonder", "what", "you", "are"],
    "abc": ["a", "b", "c", "d", "e", "f", "g"]
}

current_word_index = {song: 0 for song in songs}
current_song = None

def pronounce_and_verify(song_name: str):
    global current_word_index
    
    if song_name not in songs:
        return {"error": "Song not found"}
    
    while current_word_index[song_name] < len(songs[song_name]):
        word = songs[song_name][current_word_index[song_name]]
        
        def speak():
            engine.say(word)
            engine.runAndWait()
        
        while True:
            threading.Thread(target=speak, daemon=True).start()
            
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                print(f"Speak now: {word}")
                audio_data = recognizer.listen(source)
            
            with open("temp.wav", "wb") as f:
                f.write(audio_data.get_wav_data())
            
            result = model.transcribe("temp.wav")
            recognized_text = result["text"].strip().lower()
            os.remove("temp.wav")
            
            similarity = similarity_ratio(word.lower(), recognized_text)
            
            if similarity >= 0.8:
                current_word_index[song_name] += 1
                break
            else:
                print(f"Incorrect pronunciation. Repeating '{word}'")
    print(f"{song_name} completed")

@app.get("/start/{song_name}")
def start_practice(song_name: str):
    threading.Thread(target=pronounce_and_verify, args=(song_name,), daemon=True).start()
    return {"message": "Practice started", "song": song_name}