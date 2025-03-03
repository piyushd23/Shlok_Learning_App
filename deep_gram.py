import os
from deepgram import Deepgram
import asyncio
import json

# You'll need to install the Deepgram SDK first:
# pip install deepgram-sdk

# Set your Deepgram API key
DEEPGRAM_API_KEY = "66bd1b6344582dca9ff5332f398cf3fd64127108"

async def transcribe_audio(audio_file_path):
    # Initialize the Deepgram SDK
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        return {"error": f"File not found: {audio_file_path}"}
    
    # Open the audio file
    with open(audio_file_path, 'rb') as audio:
        # Set up options for transcription
        # Note: Deepgram automatically detects the language when you set detect_language=True
        options = {
            "smart_format": True,
            "model": "nova",  # Using Deepgram's Nova model for best accuracy
            "detect_language": True,  # Enable language detection
        }
        
        # Send the audio to Deepgram for transcription
        print(f"Transcribing file: {audio_file_path}")
        response = await deepgram.transcription.prerecorded(audio, options)
        
        # Get the detected language
        detected_language = response["results"]["channels"][0]["detected_language"]
        language_confidence = response["results"]["channels"][0]["language_confidence"]
        
        # Get the transcript
        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        
        return {
            "transcript": transcript,
            "detected_language": detected_language,
            "language_confidence": language_confidence
        }

# Example usage
async def main():
    # Replace with the path to your audio file
    audio_file_path = "temp_audio\Imagine Dragons - Thunder.mp3"
    
    result = await transcribe_audio(audio_file_path)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Detected Language: {result['detected_language']} (Confidence: {result['language_confidence']})")
        print("\nTranscript:")                 
        print(result['transcript'])

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())