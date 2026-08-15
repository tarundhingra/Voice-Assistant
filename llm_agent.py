import os
import itertools
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
from tools import get_required_documents, check_visa_status

class TravelAgent:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found in environment variables!")
            
        # 1. Initialize the new Client
        self.client = genai.Client(api_key=api_key)
        
        # 2. Set up the config with tools and system instructions
        # We explicitly disable automatic function calling to keep our custom manual loop!
        config = types.GenerateContentConfig(
            system_instruction="You are TravelBuddy, a helpful and friendly voice AI assistant. Keep your answers conversational, concise, and friendly. Do not use markdown.",
            tools=[get_required_documents, check_visa_status],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )
        
        # 3. Create the chat session
        self.chat = self.client.chats.create(
            model='gemini-3.5-flash',
            config=config
        )

    def get_response_stream(self, user_text):
        """
        Manages the stream and manually intercepts Tool Calls (Function Calling).
        """
        try:
            # 1. Send the message via stream
            response = self.chat.send_message_stream(user_text)
            
            # 2. Grab the very first chunk.
            iterator = iter(response)
            try:
                first_chunk = next(iterator)
            except StopIteration:
                return

            # 3. Check if the LLM decided to call a function
            if first_chunk.function_calls:
                # 🚨 THE FIX: Consume the rest of the stream!
                # This ensures the SDK saves the model's function_call into the chat history.
                # If we skip this, the API complains that the history is out of order.
                list(iterator) 
                
                fc = first_chunk.function_calls[0]
                print(f"\n[Agent Brain] I need to use a tool: {fc.name}()")
                
                # Safely extract the arguments the LLM provided
                args = {key: val for key, val in fc.args.items()} if fc.args else {}
                
                # Manually route to our Python functions
                if fc.name == "get_required_documents":
                    tool_result = get_required_documents(**args)
                elif fc.name == "check_visa_status":
                    tool_result = check_visa_status(**args)
                else:
                    tool_result = "Sorry, I don't know how to use that tool."
                    
                # Send the data back using the new SDK's helper method
                tool_part = types.Part.from_function_response(
                    name=fc.name,
                    response={"result": tool_result}
                )
                
                # Now ask the LLM to generate the final spoken answer based on the tool data
                final_response = self.chat.send_message_stream(tool_part)
                yield from self._extract_sentences(final_response)
                return # We are done with this turn!

            # 4. If it WASN'T a tool call, just stream the normal text!
            full_stream = itertools.chain([first_chunk], iterator)
            yield from self._extract_sentences(full_stream)
            
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            yield "Sorry, I had a problem connecting to my brain."

    def _extract_sentences(self, stream):
        """Helper function to group streaming tokens into complete sentences."""
        current_buffer = ""
        for chunk in stream:
            # Only append if it's actual text
            if chunk.text:
                current_buffer += chunk.text
                
                while any(punct in current_buffer for punct in ['. ', '? ', '! ', '\n']):
                    for punct in ['. ', '? ', '! ', '\n']:
                        if punct in current_buffer:
                            parts = current_buffer.split(punct, 1)
                            sentence = parts[0] + punct.strip()
                            
                            if sentence.strip():
                                yield sentence.strip()
                                
                            current_buffer = parts[1]
                            break
                            
        if current_buffer.strip():
            yield current_buffer.strip()