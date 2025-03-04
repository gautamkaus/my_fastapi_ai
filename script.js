const voiceInput = document.getElementById("voiceInput");
const micIcon = document.getElementById("micIcon");
const responseText = document.getElementById("responseText");
const responseAudio = document.getElementById("responseAudio");
const textInput = document.getElementById("textInput");

let recognition;
let synth = window.speechSynthesis; // Speech synthesis instance
let isProcessing = false; // Track if input is being processed
let abortController = null; // To abort ongoing fetch requests
let currentUtterance = null; // Track current speech synthesis utterance

// Check if the browser supports the Web Speech API
if ("webkitSpeechRecognition" in window) {
  recognition = new webkitSpeechRecognition();
  recognition.continuous = false; // Stop after one sentence
  recognition.interimResults = false; // Only final results
  recognition.lang = "en-US"; // Language

  recognition.onstart = () => {
    micIcon.textContent = "🎙️"; // Change icon when recording
    voiceInput.classList.add("active"); // Add active state for mic
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    console.log("Recognized text:", transcript); // Log the recognized text
    micIcon.textContent = "🎤"; // Reset icon
    voiceInput.classList.remove("active"); // Remove active state for mic
    processInput(transcript);
  };

  recognition.onerror = (event) => {
    console.error(`Speech recognition error detected: ${event.error}`);
    if (event.error === "network") {
      responseText.textContent = "Error: Network issue detected. Please check your internet connection.";
    } else {
      responseText.textContent = `Error: ${event.error}.`;
    }
    micIcon.textContent = "🎤"; // Reset icon
    voiceInput.classList.remove("active"); // Remove active state for mic
    isProcessing = false; // Reset processing state
  };
} else {
  console.error("Web Speech API not supported");
  responseText.textContent = "Error: Your browser does not support voice input.";
}

// Start voice recognition when the user taps the mic
voiceInput.addEventListener("click", () => {
  if (recognition && !isProcessing) {
    // Stop current audio playback and speech synthesis
    stopCurrentResponse();
    recognition.start();
  }
});

// Process text input
textInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !isProcessing) {
    const text = textInput.value;
    if (text.trim() !== "") {
      processInput(text);
      textInput.value = ""; // Clear the text input
    }
  }
});

// Function to process input (both voice and text)
function processInput(input) {
  isProcessing = true; // Set processing state
  micIcon.textContent = "⏳"; // Show loading state

  // Abort the previous request if it exists
  if (abortController) {
    abortController.abort();
  }

  abortController = new AbortController(); // Create a new AbortController
  sendToBackend(input, abortController.signal);
}

// Send user input to the backend
async function sendToBackend(input, signal) {
  try {
    const formData = new FormData();
    formData.append("text", input);

    // If the input is from voice, send the recorded audio file
    if (recognition && recognition.audioBlob) {
      formData.append("audio_file", recognition.audioBlob, "user_audio.wav");
    }

    const response = await fetch("https://dollar-ai.onrender.com/process_voice", {
      method: "POST",
      body: formData,
      signal,
    });

    if (!response.ok) {
      const errorData = await response.json(); // Parse error response
      throw new Error(errorData.detail || "Failed to fetch response from the backend.");
    }

    const data = await response.json();
    responseText.textContent = data.text_response; // Display the response text

    // Check if audio_response is defined
    if (!data.audio_response) {
      throw new Error("No audio response received from the backend.");
    }

    // Load audio from server endpoint
    const audioUrl = `https://dollar-ai.onrender.com/audio/${data.audio_response}`;
    loadAndPlayAudio(audioUrl);

    // Synthesize the response text to speech
    const utterance = new SpeechSynthesisUtterance(data.text_response);
    currentUtterance = utterance;
    synth.speak(utterance);
  } catch (error) {
    if (error.name === "AbortError") {
      console.log("Request aborted");
    } else {
      console.error("Error:", error);
      responseText.textContent = `Error: ${error.message}`;
    }
  } finally {
    isProcessing = false; // Reset processing state
    micIcon.textContent = "🎤"; // Reset mic icon
    abortController = null; // Reset the AbortController
  }
}
// Example function to load and play audio
async function loadAndPlayAudio(url) {
  try {
    if (!responseAudio) {
      console.error("Audio element not found in the DOM.");
      return;
    }

    // Set the audio source
    responseAudio.src = url;

    // Wait for the audio to load
    await new Promise((resolve, reject) => {
      responseAudio.oncanplay = resolve; // Resolve when the audio is ready to play
      responseAudio.onerror = reject; // Reject if there's an error loading the audio
    });

    console.log("Audio loaded successfully.");
  } catch (error) {
    console.error("Error loading audio:", error);
    responseText.textContent = "Error: Audio file not found or failed to load.";
  }
}

// Function to stop current response
function stopCurrentResponse() {
  // Stop audio playback
  responseAudio.pause();
  responseAudio.currentTime = 0;

  // Stop speech synthesis
  if (currentUtterance) {
    synth.cancel(currentUtterance);
    currentUtterance = null;
  }
}
