# TravelBuddy ✈️ - A Voice AI Assistant

Hi! I'm a student applying for a Voice AI internship, and I built this project to learn how end-to-end conversational voice agents actually work. 

TravelBuddy is a locally-run Voice AI assistant that helps users with travel and visa queries. It listens to your voice, thinks using an LLM, uses tools to look up mock database records, and speaks the answer back to you. It even has basic interruption handling (if you talk while it's speaking, it stops!).

## 🛠️ What it uses
* **Speech-to-Text (STT):** `faster-whisper` (running locally on CPU) + `SpeechRecognition`
* **Brain & Reasoning:** Gemini API (`gemini-1.5-flash`) via the `google-generativeai` package.
* **Tool Calling:** Gemini is hooked up to python functions that read from a local `mock_data.json` file to check visa statuses and required documents.
* **Text-to-Speech (TTS):** `gTTS` (Google Text-to-Speech) played through `pygame` (which allows for easy stopping).
* **Interruption Handling (VAD):** A basic `pyaudio` volume threshold check.

## 🚀 How to run it

1. **Clone the repo and enter the folder.**
2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate

            ## 🧠 What I learned building this
         * **Sentence-Level Streaming is a game-changer:** Originally, the bot waited for the entire paragraph to generate before speaking. By changing the LLM to yield tokens (`stream=True`) and splitting them by punctuation, I was able to pass individual sentences into a Queue. Now, the bot starts speaking the first sentence while the LLM is still generating the third one!
         * **Silero VAD vs Volume Thresholds:** My first VAD implementation just checked if the mic was loud. It was terrible—coughing or keyboard typing would cut the bot off. I swapped it for **Silero VAD**, an enterprise-grade neural network that processes 32ms audio chunks to specifically detect *human speech probabilities*. It's infinitely more robust.
         * **Concurrency in Python:** Getting the generator thread, the playback thread, and the microphone monitoring loop to all run concurrently without blocking each other was a fantastic lesson in `threading.Event()` and thread safety.

Manual Tool Calling under the hood: I ran into a limitation where the Gemini SDK doesn't support streaming and automatic function calling simultaneously. Instead of giving up on streaming, I disabled auto-tools and built my own manual tool-dispatch loop. Now, my code parses the stream chunks, intercepts the LLM's function_call requests, executes the Python function, and passes the result back to the LLM to stream the final spoken answer. It taught me exactly how AI Agents think and act!