import assemblyai as aai

aai.settings.api_key = "beb812897c954033a0c986f0f2bd7c25"
transcriber = aai.Transcriber()

transcript = transcriber.transcribe("temp_audio\Imagine Dragons - Thunder.mp3")

print(transcript.text)