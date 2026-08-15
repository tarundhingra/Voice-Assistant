import speech_recognition as sr
from faster_whisper import WhisperModel
import tempfile
import os
import numpy as np
import pyaudio
import torch
from silero_vad import load_silero_vad

print("Loading Whisper model...")
model = WhisperModel("tiny.en", device="cpu", compute_type="int8")

# Load Silero VAD once globally
print("Loading Silero VAD model...")
vad_model = load_silero_vad(onnx=False) 

def listen_and_transcribe():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nAdjusting for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening... (Speak now)")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("Processing speech...")

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio.get_wav_data())
                temp_filename = f.name

            segments, _ = model.transcribe(temp_filename, beam_size=5)
            text = "".join([segment.text for segment in segments])

            os.remove(temp_filename)
            return text.strip()
        except sr.WaitTimeoutError:
            return "" 
        except Exception as e:
            print(f"STT Error: {e}")
            return ""

def is_user_speaking(threshold=0.6):
    """
    UPGRADED: Uses Silero VAD (a neural network) instead of raw volume.
    It returns a probability between 0.0 and 1.0 of whether it hears a human voice.
    """
    try:
        p = pyaudio.PyAudio()
        # Silero VAD requires exactly 16000 Hz sample rate
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=512)
        
        # Read ~3 quick chunks (about 100ms) to see if anyone is speaking right now
        for _ in range(3):
            data = stream.read(512, exception_on_overflow=False)
            
            # Convert 16-bit PCM to float32 tensor, which Silero expects
            audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            tensor_data = torch.from_numpy(audio_data)
            
            # Pass to Silero model to get speech probability
            speech_prob = vad_model(tensor_data, 16000).item()
            
            if speech_prob > threshold:
                stream.close()
                p.terminate()
                return True
                
        stream.close()
        p.terminate()
        return False
    except Exception:
        return False