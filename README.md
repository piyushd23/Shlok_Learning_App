# Learning App Backend

This is a FastAPI backend for a language learning app that allows users to select a song, hear pronunciation guidance, repeat words via microphone, and receive feedback on pronunciation correctness.

## Features
- Retrieve a list of available songs.
- Get words from a selected song.
- Hear pronunciation of words using text-to-speech.
- Verify pronunciation accuracy using Whisper AI and Speech Recognition.

## Installation

### Prerequisites
- Python 3.8+
- Install dependencies:
  ```sh
  pip install fastapi uvicorn whisper pyttsx3 speechrecognition
  ```
- Install Whisper model:
  ```sh
  pip install openai-whisper
  ```
  Or download it manually:
  ```sh
  whisper.load_model("base")
  ```

## Running the Server
Run the FastAPI server with:
```sh
uvicorn main:app --reload
```

## API Documentation
FastAPI automatically generates API documentation:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Endpoints

### 1. Get List of Songs
**Request:**
```
GET /songs
Headers:
  Content-Type: application/json
Body: None
```
**Response:**
```
200 OK
{
  "songs": ["song1", "song2"]
}
```

### 2. Get Words for a Song
**Request:**
```
GET /song/{song_name}
Headers:
  Content-Type: application/json
Body: None
```
**Example:**
```
GET /song/song1
```
**Response:**
```
200 OK
{
  "words": ["hello", "world"]
}
```
_If song not found:_
```
404 Not Found
{
  "detail": "Song not found"
}
```

### 3. Pronounce a Word
**Request:**
```
GET /pronounce/{word}
Headers:
  Content-Type: application/json
Body: None
```
**Example:**
```
GET /pronounce/hello
```
**Response:**
```
200 OK
{
  "message": "Pronounced hello"
}
```

### 4. Verify Pronunciation
**Request:**
```
POST /verify
Headers:
  Content-Type: application/json
Body: None (Microphone audio is recorded)
```
**Response:**
```
200 OK
{
  "recognized": "hello",
  "correct": true,
  "similarity": 0.9,
  "best_match": "hello"
}
```
_If an error occurs:_
```
500 Internal Server Error
{
  "detail": "Error message"
}
```

## Contributing
Feel free to contribute by submitting issues or pull requests.

## License
This project is licensed under the MIT License.

