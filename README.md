TravelBuddy ✈️ | End-to-End Voice AI Travel Assistant
Hi! I built this project because I wanted to get my hands dirty and learn how conversational voice agents actually work under the hood.

TravelBuddy is a locally-run Voice AI assistant designed to handle travel and visa queries. It listens to your voice, thinks through the logic using an LLM, dynamically fetches data from mock database records, and speaks the answer back to you. It even supports "barge-in"—if you interrupt it while it's talking, it immediately stops and listens.

🛠️ Tech Stack & Architecture
I started with a basic turn-based script, but quickly upgraded it to a multi-threaded streaming architecture to make it feel like a real conversation.

Speech-to-Text (STT): faster-whisper running locally on CPU.

Brain & Reasoning: Gemini 3.5 flash-lite via the new google-genai SDK.

Tool Calling: Custom manual dispatch loop hooked up to Python functions that read from a local mock_data.json file (simulating checking visa statuses and requirements).

Text-to-Speech (TTS): gTTS played through pygame for easy asynchronous audio control.

Interruption Handling (VAD): Silero VAD, an enterprise-grade neural network that detects actual human speech probabilities, bypassing background noise.

🚀 How to Run It Locally
Clone the repo and enter the folder.

Create and activate a virtual environment:

Bash
uv venv --python 3.12
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate
Install the dependencies:

Bash
uv pip install -r requirements.txt
Set your Gemini API Key:

Bash
# On Windows:
set GEMINI_API_KEY="your_api_key_here"
# On Mac/Linux:
export GEMINI_API_KEY="your_api_key_here"
Start talking to the assistant:

Bash
python main.py
🧠 The Biggest Engineering Lessons
Building this taught me that hooking up APIs is easy, but making a voice agent feel natural and fast is a serious engineering challenge. Here are my biggest takeaways:

Sentence-Level Streaming is a game-changer: Originally, the bot waited for the entire LLM paragraph to generate before generating the MP3. By changing the LLM to yield tokens (stream=True) and splitting them by punctuation, I was able to pass individual sentences into a Queue. Now, the bot starts speaking the first sentence while the LLM is still generating the third one!

Silero VAD vs. Simple Volume Thresholds: My first interruption script just checked if the mic was loud. It was terrible—typing on my keyboard or a loud car driving by would cut the bot off. I swapped it out for Silero VAD, which processes raw 32ms audio chunks to detect human speech probabilities. It made the "barge-in" feature infinitely more robust.

Manual Tool Calling is better than auto-magic: I ran into a limitation where the Gemini SDK doesn't support streaming and automatic function calling at the same time. Instead of giving up on streaming, I disabled auto-tools and built my own manual tool-dispatch loop. Now, my code parses the stream chunks, intercepts the LLM's function_call requests, executes the Python function, and passes the result back to the LLM to stream the final spoken answer. It forced me to learn exactly how AI Agents maintain chat history and state.

Concurrency in Python: Getting the LLM generator thread, the audio playback thread, and the microphone monitoring loop to all run concurrently without blocking each other was a fantastic lesson in threading.Event(), queues, and thread safety.

🔮 What I'd Do Next
If I had more time to expand this for production, I would swap gTTS for a faster, streaming-native TTS service (like ElevenLabs or Cartesia) and hook the tools up to a live SQL database or a real travel API instead of a mock JSON file.
