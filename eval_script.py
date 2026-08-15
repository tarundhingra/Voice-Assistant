import time
from llm_agent import TravelAgent

def run_eval():
    print("Starting tiny eval script...\n")
    agent = TravelAgent()

    test_cases = [
        "Hi, I'm planning a trip.",
        "What documents do I need for a Schengen visa?",
        "Can you check the status of my application? The ID is APP123.",
        "How about application APP404?",
        "What documents do I need for a USA visa?"
    ]

    for i, text in enumerate(test_cases):
        print(f"Test {i+1}: {text}")
        start_time = time.time()

        response = agent.get_response(text)

        end_time = time.time()
        latency = end_time - start_time

        print(f"Response: {response}")
        print(f"Latency: {latency:.2f} seconds")

        # A simple manual checklist for me to review later
        print("\nManual Checklist:")
        print("[ ] Did it sound natural?")
        print("[ ] Did it hallucinate any policies/data?")
        print("[ ] If a tool was needed, did it call it correctly? (Check console output)")
        print("-" * 50)

if __name__ == "__main__":
    run_eval()