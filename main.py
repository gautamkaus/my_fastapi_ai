from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import os
import aiohttp
import asyncio
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.staticfiles import StaticFiles
# Load environment variables
load_dotenv()
app = FastAPI()

app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

# Configure logging
logging.basicConfig(level=logging.DEBUG)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Predefined intents and responses
PREDEFINED_INTENTS = {
    "hello": "Hello! How can I assist you today?",
    "how are you": "I'm just a bot, but I'm doing great! How about you?",
    "what is your name": "I am your personal assistant Dollar.",
    "goodbye": "Goodbye! Have a great day!",
    "thank you": "You're welcome!",
    "what's the weather": "Please provide your location, and I'll check the weather for you.",
    "help": "Of course! What do you need help with?",
    "who are you":"I am your assistant Dollar ,I am created by Kaustubh Gautam.",
}

# Function to convert text to voice
def text_to_voice(text: str, output_file_path: str):
    engine.save_to_file(text, output_file_path)
    engine.runAndWait()

# Function to convert voice to text
def voice_to_text(audio_file_path: str) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand the audio")
    except sr.RequestError:
        raise HTTPException(status_code=500, detail="Speech recognition service failed")

# Fetch response from OpenRouter API asynchronously
async def get_openrouter_response(prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek/deepseek-r1",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": 1000,
                }
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenRouter API error: {str(e)}")

# Process text or voice input asynchronously
@app.post("/process_voice")
async def process_voice(text: str = Form(None), audio_file: UploadFile = File(None)):
    try:
        # Determine if the input is text or voice
        if text:
            logging.debug(f"Text input: {text}")
        elif audio_file:
            logging.debug("Processing audio file")
            audio_file_path = "user_audio.wav"
            with open(audio_file_path, "wb") as buffer:
                buffer.write(audio_file.file.read())
            text = voice_to_text(audio_file_path)
            os.remove(audio_file_path)
            logging.debug(f"Recognized text: {text}")
        else:
            raise HTTPException(status_code=400, detail="No input provided")

        # Check for predefined intents
        text_lower = text.lower()
        if text_lower in PREDEFINED_INTENTS:
            response = PREDEFINED_INTENTS[text_lower]
            logging.debug(f"Predefined intent matched: {response}")
        else:
            logging.debug("Fetching response from OpenRouter")
            response = await get_openrouter_response(text)

        # Convert response to voice and save temporarily
        response_audio_path = f"response_audio_{os.urandom(16).hex()}.wav"
        logging.debug("Converting response to audio")
        text_to_voice(response, response_audio_path)

        # Save audio file to accessible directory
        audio_dir = "audio_files"
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        os.rename(response_audio_path, f"{audio_dir}/{response_audio_path}")

        # Return the response
        return {
            "text_input": text,
            "text_response": response,
            "audio_response": response_audio_path
        }
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Endpoint to serve saved audio files
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    try:
        audio_path = os.path.join("audio_files", filename)
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail=f"Audio file '{filename}' not found")
        return FileResponse(audio_path, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Audio file not found")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Hello, World!"}
