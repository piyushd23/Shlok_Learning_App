import torch
import torchaudio
import librosa
import numpy as np
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from torch import hub

class VocalTranscriber:
    def __init__(self):
        # Initialize Demucs for source separation using torch hub
        self.separator = hub.load('facebookresearch/demucs', 'htdemucs')
        if torch.cuda.is_available():
            self.separator.cuda()
        
        # Initialize Wav2Vec2 for speech recognition
        self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
        self.model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
        
    def separate_vocals(self, audio_path):
        """Extract vocals from the music file using Demucs."""
        # Load audio
        wav, sr = torchaudio.load(audio_path)
        
        # Convert to mono if stereo
        if wav.shape[0] > 1:
            wav = torch.mean(wav, dim=0, keepdim=True)
        
        # Adjust audio length to be compatible with the model
        wav = wav.reshape(1, -1)  # Add batch dimension
        
        # Apply source separation
        with torch.no_grad():
            sources = self.separator.forward(wav)
            # sources is (batch, source, channels, time)
            vocals = sources[0, 0]  # Extract vocals
        
        return vocals.cpu().numpy(), sr
    
    def transcribe_vocals(self, vocals, sample_rate):
        """Transcribe the separated vocals using Wav2Vec2."""
        # Resample if necessary (Wav2Vec2 expects 16kHz)
        if sample_rate != 16000:
            vocals = librosa.resample(vocals, orig_sr=sample_rate, target_sr=16000)
        
        # Normalize audio
        vocals = (vocals - np.mean(vocals)) / np.std(vocals)
        
        # Prepare input features
        inputs = self.processor(vocals, sampling_rate=16000, return_tensors="pt", padding=True)
        
        # Get logits
        with torch.no_grad():
            logits = self.model(inputs.input_values).logits
        
        # Decode predicted ids to text
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(predicted_ids)
        
        return transcription[0]
    
    def process_file(self, audio_path):
        """Process an audio file to transcribe vocals."""
        print("Separating vocals from music...")
        vocals, sr = self.separate_vocals(audio_path)
        
        print("Transcribing vocals...")
        transcription = self.transcribe_vocals(vocals, sr)
        
        return transcription

def main():
    # Example usage
    transcriber = VocalTranscriber()
    
    # Change this to your MP3 file path
    audio_path = "D:/Shlok/temp_audio/Imagine Dragons - Thunder.mp3"
    
    try:
        transcription = transcriber.process_file(audio_path)
        print("\nTranscription:")
        print(transcription)
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()