import threading
import time
import queue
import os
import pygame
from stt import listen_and_transcribe, is_user_speaking
from tts import speak_to_file, play_audio, stop_speaking
from llm_agent import TravelAgent

def main():
    print("--- Welcome to TravelBuddy! ---")
    print("Initializing AI Agent...")
    agent = TravelAgent()
    print("Ready! Say 'exit' or 'quit' to stop.")

    while True:
        # 1. Listen
        user_text = listen_and_transcribe()
        if not user_text:
            continue

        print(f"\nYou: {user_text}")

        if "exit" in user_text.lower() or "quit" in user_text.lower():
            print("TravelBuddy: Bye! Have a great trip.")
            filename = speak_to_file("Bye! Have a great trip.")
            if filename: play_audio(filename)
            break

        # 2. Think & Speak (Streaming!)
        print("TravelBuddy is thinking...")
        
        # This queue holds the generated audio chunks
        audio_queue = queue.Queue()
        stop_event = threading.Event()
        
        # Thread 1: Stream LLM sentences and convert them to audio files
        def generate_audio_stream():
            for sentence in agent.get_response_stream(user_text):
                if stop_event.is_set():
                    break
                print(f"TravelBuddy: {sentence}")
                
                filename = speak_to_file(sentence)
                if filename:
                    audio_queue.put(filename)
                    
            # Put None in the queue to signal we are completely done generating
            audio_queue.put(None) 
            
        # Thread 2: Play the audio files one by one as they arrive
        def play_audio_stream():
            while not stop_event.is_set():
                try:
                    # Timeout prevents this from freezing if generation is slow
                    filename = audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                    
                if filename is None:
                    break # Reached the end of the response
                    
                play_audio(filename)
                
                # Wait for this sentence to finish playing before moving to the next
                while pygame.mixer.music.get_busy() and not stop_event.is_set():
                    time.sleep(0.1)
                    
                # Clean up the file
                try:
                    os.remove(filename)
                except:
                    pass

        gen_thread = threading.Thread(target=generate_audio_stream)
        play_thread = threading.Thread(target=play_audio_stream)
        
        gen_thread.start()
        play_thread.start()

        # 3. Monitor for interruptions in the main thread!
        time.sleep(1.0) # Grace period so it doesn't interrupt itself from speaker echo
        
        # While either generation or playback is happening, listen for human speech
        while gen_thread.is_alive() or play_thread.is_alive():
            if is_user_speaking(threshold=0.6):
                print("\n[Interrupted! Silero VAD detected human speech]")
                stop_event.set() # Stop the threads
                stop_speaking()  # Stop the audio playback
                break
            time.sleep(0.1)
            
        gen_thread.join()
        play_thread.join()

if __name__ == "__main__":
    main()