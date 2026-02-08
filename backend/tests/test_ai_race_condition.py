import sys
import os
import asyncio
import pytest
from unittest.mock import MagicMock, patch

# Ensure backend is in path
sys.path.append(os.path.abspath("backend"))

# Mock dependencies that are missing in the environment
sys.modules['openai'] = MagicMock()
sys.modules['langchain_text_splitters'] = MagicMock()
sys.modules['pydantic_settings'] = MagicMock()
sys.modules['app.config'] = MagicMock()

from app.services import ai

def test_race_condition():
    """
    Test that concurrent calls to generate_notes_map_reduce do not interfere with each other's token tracking.
    """
    asyncio.run(_run_async_test())

async def _run_async_test():
    # Mock client response with delay to force concurrency overlap
    async def delayed_response(*args, **kwargs):
        await asyncio.sleep(0.1)
        mock_response = MagicMock()
        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=10)
        mock_response.choices = [MagicMock(message=MagicMock(content="Mocked response"))]
        return mock_response

    # Patch the client instance method used in ai.py
    ai.client.chat.completions.create.side_effect = delayed_response

    # Patch RecursiveCharacterTextSplitter
    with patch('app.services.ai.RecursiveCharacterTextSplitter') as MockSplitter:
        instance = MockSplitter.return_value
        instance.split_text.return_value = ["chunk1", "chunk2"]

        # Run 2 concurrent requests
        segments = [{"text": "video content"}]

        task1 = asyncio.create_task(ai.generate_notes_map_reduce(segments))
        task2 = asyncio.create_task(ai.generate_notes_map_reduce(segments))

        results = await asyncio.gather(task1, task2)

        stats1 = results[0][1]
        stats2 = results[1][1]

        # Assertions
        assert stats1['input_tokens'] == 30, f"Expected 30 input tokens for task 1, got {stats1['input_tokens']}"
        assert stats1['output_tokens'] == 30, f"Expected 30 output tokens for task 1, got {stats1['output_tokens']}"

        assert stats2['input_tokens'] == 30, f"Expected 30 input tokens for task 2, got {stats2['input_tokens']}"
        assert stats2['output_tokens'] == 30, f"Expected 30 output tokens for task 2, got {stats2['output_tokens']}"
