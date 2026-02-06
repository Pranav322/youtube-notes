import asyncio
import os
import sys

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai import generate_notes_map_reduce
from dotenv import load_dotenv

load_dotenv()

# Mock transcript segments (shortened for test)
MOCK_SEGMENTS = [
    {"text": "Welcome to this Python tutorial.", "start": 0.0, "duration": 5.0},
    {"text": "We will learn about lists today.", "start": 5.0, "duration": 5.0},
    {"text": "Here is a list: my_list = [1, 2, 3]", "start": 10.0, "duration": 5.0},
    {"text": "Lists are mutable sequences.", "start": 15.0, "duration": 5.0},
]

async def test_map_reduce():
    print("Testing Map-Reduce Generation...")
    try:
        if not os.getenv("AZURE_OPENAI_API_KEY"):
            print("Skipping test: AZURE_OPENAI_API_KEY not found in env")
            return

        output = await generate_notes_map_reduce(MOCK_SEGMENTS)
        print("Success! Output preview:")
        print(output[:200] if output else "No output generated")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_map_reduce())
