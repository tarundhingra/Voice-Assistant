from gtts import gTTS
import pygame
import os
import uuid

pygame.mixer.init()

def speak_to_file(text):
    """
    Generates speech and saves it to a file. 
    Returning the filename lets the main script queue it up for streaming!
    """
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        # Give it a random filename so chunks don't overwrite each other
        filename = f"temp_reply_{uuid.uuid4().hex[:6]}.mp3"
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"TTS error: {e}")
        return None

def play_audio(filename):
    """Starts playing a specific audio file."""
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    except Exception as e:
        pass

def stop_speaking():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()