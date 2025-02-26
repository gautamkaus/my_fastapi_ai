# Dollar AI - FastAPI Voice Assistant

## Overview

This project is a voice and text-based personal AI assistant called Dollar, built using FastAPI, OpenAI, SpeechRecognition, and pyttsx3. It allows users to interact with an AI assistant via text or voice, get responses, and have those responses spoken back to them. User interactions are stored in a PostgreSQL database.
## Explanation Tutorial
**https://drive.google.com/drive/folders/1BxvAnGcWxXpbnwQn8lh1t3Uty29bpeir?usp=sharing**
## Features

*   **Text and Voice Input:** Users can interact with the AI using either text or voice commands.
*   **AI-Powered Responses:**  Leverages the OpenAI API via OpenRouter to generate intelligent and helpful responses.
*   **Text-to-Speech:** Converts AI-generated text responses into spoken audio using `pyttsx3`.
*   **Speech-to-Text:** Converts user voice input into text using the `speech_recognition` library.
*   **Persistent Storage:** Stores all interactions (user input, AI response, and audio file paths) in a PostgreSQL database using SQLAlchemy.
*   **Predefined Intents:** Handles common requests (hello, goodbye, etc.) with pre-programmed responses for faster interaction.
*   **Asynchronous Processing:** Utilizes `asyncio` and `aiohttp` for efficient handling of API requests and audio processing.
*   **Web Interface:** Provides a simple web interface for interacting with the assistant.

## Technologies Used

*   [FastAPI](https://fastapi.tiangolo.com/):  A modern, fast (high-performance), web framework for building APIs with Python 3.7+
*   [OpenAI API](https://openai.com/api/): Used for generating AI responses (via OpenRouter).
*   [OpenRouter](https://openrouter.ai/): Used for accessing the OpenAI API
*   [SpeechRecognition](https://pypi.org/project/SpeechRecognition/):  For converting speech to text.
*   [pyttsx3](https://pypi.org/project/pyttsx3/): For converting text to speech.
*   [SQLAlchemy](https://www.sqlalchemy.org/):  For interacting with the PostgreSQL database.
*   [PostgreSQL](https://www.postgresql.org/):  The database used to store interaction history.
*   [Uvicorn](https://www.uvicorn.org/):  An ASGI server for running the FastAPI application.
*   [JavaScript](https://www.javascript.com/): Used for the frontend web interface.
*   [Docker](https://www.docker.com/): Used for containerization.
*   [Docker Compose](https://docs.docker.com/compose/): Used for defining and running multi-container Docker applications.

## Setup and Installation

1.  **Clone the repository:**

    ```
    git clone https://github.com/gautamkaus/my_fastapi_ai.git
    cd my_fastapi_ai
    ```

2.  **Create a virtual environment (recommended):**

    ```
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install the dependencies:**

    ```
    pip install -r requirements.txt
    ```

4.  **Configuration:**

    *   Create a `.env` file in the root directory of the project.
    *   Add the following environment variables to the `.env` file:

        ```
        OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
        DATABASE_URL=postgresql://your_user:your_password@your_host:5432/your_database
        ```

        *   Replace `YOUR_OPENROUTER_API_KEY` with your actual OpenRouter API key.
        *   Replace the database credentials with your PostgreSQL database credentials.

5.  **Database Setup:**

    *   Ensure you have PostgreSQL installed and running.
    *   Create a database with the name specified in your `DATABASE_URL`.

6.  **Run the Application:**

    ```
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

    *   The `--reload` flag enables automatic reloading of the server on code changes (useful for development).

7. **Access the Web Interface:**

    * Open your web browser and navigate to `http://localhost:8000`.

## Docker Deployment (Recommended)

1.  **Build the Docker image:**

    ```
    docker build -t dollar-ai .
    ```

2.  **Run the Docker container using Docker Compose:**

    ```
    docker-compose up -d
    ```

    *   This command will build and run the application using the `docker-compose.yml` file.  Make sure you have a `docker-compose.yml` file configured properly.

3.  **Access the Web Interface:**

    *   Open your web browser and navigate to `http://localhost:8000`.

## Code Structure

*   `main.py`:  The main FastAPI application file, containing the API endpoints, logic for handling requests, and integration with OpenAI, SpeechRecognition, and pyttsx3.
*   `database.py`: Defines the database models (using SQLAlchemy) and the database connection logic.
*   `requirements.txt`:  Lists the Python dependencies required for the project.
*   `static/`: Contains static files such as the HTML, CSS, and JavaScript files for the frontend.
*   `audio_files/`:  (Dynamically created) Stores the generated audio files.
*   `docker-compose.yml`: (Optional, but highly recommended) Defines the services, networks, and volumes for running the application using Docker Compose.
*   `.env`: Stores the sensitive information for the project like API keys, database URLs, etc. (Make sure to add this file to your `.gitignore`)

## Contributing

Feel free to contribute to this project by submitting pull requests.


