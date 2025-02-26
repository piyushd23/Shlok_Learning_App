import whisper
from thefuzz import fuzz

# Load Whisper model once to avoid reloading for every request
model = whisper.load_model("base")

def verify_pronunciation(audio_file, expected_text):
    """
    Transcribes the user's audio and compares it with the expected text.
    Uses fuzzy matching to allow slight pronunciation variations.
    """
    file_path = "temp_audio.wav"
    audio_file.save(file_path)

    # Transcribe audio
    result = model.transcribe(file_path)
    transcribed_text = result["text"].strip()

    # Use fuzzy matching to compare similarity
    similarity_score = fuzz.ratio(transcribed_text, expected_text)

    # Define a threshold for acceptance (e.g., 80% similarity)
    is_correct = similarity_score >= 80

    return {
        "recognized": transcribed_text,
        "correct": is_correct,
        "similarity_score": similarity_score
    }
