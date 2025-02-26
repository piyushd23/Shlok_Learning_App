from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import pyttsx3
import os
import speech_recognition as sr
from difflib import SequenceMatcher
import asyncio
import functools
import time
import logging
from contextlib import contextmanager
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware to handle frontend interruptions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize with error handling
try:
    engine = pyttsx3.init()
    model = whisper.load_model("base")  # Load Whisper model
    recognizer = sr.Recognizer()
    logger.info("Successfully initialized all components")
except Exception as e:
    logger.error(f"Failed to initialize components: {str(e)}")
    # We'll create fallback mechanisms later

# Pre-stored song list
songs = {
    "song1": ["hello", "world"],
    "song2": ["fast", "API"]
}

# Timeout decorator to handle long-running operations
def timeout_handler(seconds):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # For async functions
                if asyncio.iscoroutinefunction(func):
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
                # For sync functions
                else:
                    return await asyncio.wait_for(asyncio.to_thread(func, *args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {seconds} seconds")
                raise HTTPException(status_code=504, detail="Operation timed out")
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        return wrapper
    return decorator

# Resource cleanup context manager
@contextmanager
def resource_cleanup(resource_name, resource=None):
    try:
        yield
    except Exception as e:
        logger.error(f"Error with {resource_name}: {str(e)}")
        # Implement specific cleanup based on resource type
        if resource_name == "temp_file" and resource:
            try:
                if os.path.exists(resource):
                    os.remove(resource)
                    logger.info(f"Cleaned up {resource}")
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up {resource}: {str(cleanup_error)}")
        raise
    finally:
        # Always execute cleanup for specific resources
        if resource_name == "temp_file" and resource:
            try:
                if os.path.exists(resource):
                    os.remove(resource)
                    logger.info(f"Cleaned up {resource}")
            except Exception as e:
                logger.error(f"Failed in finally block to clean up {resource}: {str(e)}")

def similarity_ratio(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

# Global exception handler
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Global exception: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred", "error": str(e)}
        )

# Health check endpoint to verify service is running
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/songs")
def get_songs():
    try:
        return {"songs": list(songs.keys())}
    except Exception as e:
        logger.error(f"Error fetching songs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve songs: {str(e)}")

@app.get("/song/{song_name}")
def get_song_words(song_name: str):
    try:
        if song_name not in songs:
            raise HTTPException(status_code=404, detail="Song not found")
        return {"words": songs[song_name]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching song {song_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve song details: {str(e)}")

@app.get("/pronounce/{word}")
@timeout_handler(10)  # Set appropriate timeout
async def pronounce_word(word: str):
    try:
        def say_word():
            engine.say(word)
            engine.runAndWait()
            
        # Run text-to-speech in a separate thread to prevent blocking
        await asyncio.to_thread(say_word)
        return {"message": f"Pronounced {word}"}
    except Exception as e:
        logger.error(f"Error pronouncing word {word}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to pronounce word: {str(e)}")

@app.post("/verify")
@timeout_handler(30)  # Speech recognition may take longer
async def verify_pronunciation():
    temp_file = "temp.wav"
    
    try:
        with resource_cleanup("temp_file", temp_file):
            # Recording audio
            try:
                audio_data = await asyncio.to_thread(record_audio)
            except Exception as e:
                logger.error(f"Error recording audio: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to record audio")
            
            # Save audio file
            try:
                with open(temp_file, "wb") as f:
                    f.write(audio_data.get_wav_data())
            except Exception as e:
                logger.error(f"Error saving audio file: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to save audio file")
            
            # Transcribe with Whisper
            try:
                result = await asyncio.to_thread(lambda: model.transcribe(temp_file))
                recognized_text = result["text"].strip().lower()
            except Exception as e:
                logger.error(f"Error transcribing audio: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to transcribe audio")
            
            # Compare with correct words
            correct_words = [word.lower() for word in songs.get("song1", [])]
            best_match = max(correct_words, key=lambda w: similarity_ratio(w, recognized_text))
            similarity = similarity_ratio(best_match, recognized_text)
            
            return {
                "recognized": recognized_text, 
                "correct": similarity >= 0.8, 
                "similarity": similarity, 
                "best_match": best_match
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in verify_pronunciation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

# Helper function for audio recording with retry logic
def record_audio(max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            with sr.Microphone() as source:
                logger.info("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source)
                logger.info("Speak now...")
                return recognizer.listen(source, timeout=10, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            retries += 1
            logger.warning(f"No speech detected, retry {retries}/{max_retries}")
            if retries >= max_retries:
                raise HTTPException(status_code=408, detail="No speech detected after multiple attempts")
        except Exception as e:
            logger.error(f"Error recording audio: {str(e)}")
            raise

# Shutdown event handler to clean up resources
@app.on_event("shutdown")
def shutdown_event():
    try:
        logger.info("Shutting down application, cleaning up resources...")
        # Clean up any temporary files that might still exist
        if os.path.exists("temp.wav"):
            os.remove("temp.wav")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)