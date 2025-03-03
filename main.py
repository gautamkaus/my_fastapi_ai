from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os
import aiohttp
import asyncio
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
import logging
from datetime import datetime
from database import Interaction, get_db
from sqlalchemy.orm import Session
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize FastAPI app
app = FastAPI()

# Mount static files for audio
app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

# Configure CORS
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
    "who are you": "I am your assistant Dollar, created by Kaustubh Gautam.",
    "what can you do": "I can help you with tasks like answering questions, telling jokes, checking the weather, and more!",
    "what are your features": "I can assist with information, provide recommendations, tell jokes, and much more. Just ask!",
    "i don't understand": "I'm sorry, I didn't get that. Could you please rephrase?",
    "what does that mean": "Could you clarify? I want to make sure I understand you correctly.",
    "good night": "Good night! Sleep well and sweet dreams!",
    "goodnight": "Goodnight! Have a peaceful sleep!",
    "who created you": "I was created by Kaustubh Gautam.",
    "bye": "Bye! See you later!",
    "see you later": "See you later! Take care!"

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
async def get_openai_response(prompt: str) -> str:
    
    # Fetch the API key from environment variables
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

    try:
        # Initialize the OpenAI client with custom base URL
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.sree.shop/v1"
        )

        # Create a completion using the OpenAI client
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=False  # Ensure streaming is disabled
        )

        # Handle non-streaming response
        if not completion.choices or len(completion.choices) == 0:
            raise HTTPException(status_code=500, detail="Invalid API response: No choices found")

        # Extract the response content
        response = completion.choices[0].message.content

        # Check if the response is empty
        if not response:
            raise HTTPException(status_code=500, detail="Invalid API response: No content found")

        return response.strip()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenRouter API error: {str(e)}")

# Process text or voice input asynchronously
@app.post("/process_voice")
async def process_voice(
    text: str = Form(None),
    audio_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        user_input_voice_path = None

        # Determine if the input is text or voice
        if text:
            logging.debug(f"Text input: {text}")
        elif audio_file:
            logging.debug("Processing audio file")
            user_input_voice_path = f"user_audio_{os.urandom(16).hex()}.wav"
            with open(user_input_voice_path, "wb") as buffer:
                buffer.write(await audio_file.read())
            text = voice_to_text(user_input_voice_path)
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
            response = await get_openai_response(text)

        # Convert response to voice and save temporarily
        response_audio_path = f"response_audio_{os.urandom(16).hex()}.wav"
        logging.debug("Converting response to audio")
        text_to_voice(response, response_audio_path)

        # Save audio file to accessible directory
        audio_dir = "audio_files"
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        os.rename(response_audio_path, f"{audio_dir}/{response_audio_path}")

        # Store interaction in the database
        interaction = Interaction(
            user_input_text=text,
            user_input_voice_path=user_input_voice_path if audio_file else None,
            response_text=response,
            response_voice_path=f"{audio_dir}/{response_audio_path}",
            created_at=datetime.utcnow()
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        # Return the response
        return {
            "text_input": text,
            "text_response": response,
            "audio_response": response_audio_path  # Ensure this is always defined
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


# Define a route to serve the main HTML file
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)
        

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Hello, World!"}
