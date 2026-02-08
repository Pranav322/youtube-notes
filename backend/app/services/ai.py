from openai import AsyncAzureOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings
import logging
import asyncio

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure OpenAI Client
client = AsyncAzureOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
)

# Shared text splitter to avoid re-instantiation on every request
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=400,
    length_function=len,
)

MAP_PROMPT = """You are a Senior Technical Writer. Convert the following transcript segment into clean, structured Markdown notes.

Transcript Segment:
{text}

Rules:
- Output pure Markdown only.
- Use '###' for sub-section headers based on topic shifts.
- Preserve any described code into proper Markdown code blocks with language tags.
- Preserve mathematical expressions as formulas.
- Use bullet points for step-by-step processes.
- Bold important terms and concepts.
- Remove conversational filler.
- Focus strictly on technical content.
"""

REDUCE_PROMPT = """You are a Senior Technical Editor. You have been given a set of Markdown notes generated from transcript chunks of a video.
Your goal is to synthesize them into a single, cohesive technical document.

Input Notes:
{text}

Rules:
1. Remove redundant explanations across chunks.
2. Ensure logical flow from introduction to conclusion.
3. Generate a concise Table of Contents at the top.
4. Maintain all code blocks and formulas found in the notes.
5. Output pure Markdown.
6. Add a Title at the very top.
7. Do not summarize the code; keep the full snippets if they are technical examples.
"""

# GPT-4.1 pricing (Azure OpenAI - Standard/Global, per 1K tokens)
# Source: https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/
COST_PER_1K_INPUT = 0.002    # $2.00 per 1M input tokens
COST_PER_1K_OUTPUT = 0.008   # $8.00 per 1M output tokens

# Track total tokens across a generation run
class TokenTracker:
    def __init__(self):
        self.total_input = 0
        self.total_output = 0
    
    def add(self, input_tokens: int, output_tokens: int):
        self.total_input += input_tokens
        self.total_output += output_tokens
    
    def get_cost(self) -> float:
        input_cost = (self.total_input / 1000) * COST_PER_1K_INPUT
        output_cost = (self.total_output / 1000) * COST_PER_1K_OUTPUT
        return input_cost + output_cost
    
    def get_stats(self) -> dict:
        return {
            "input_tokens": self.total_input,
            "output_tokens": self.total_output,
            "cost": self.get_cost()
        }
    
    def log_summary(self):
        cost = self.get_cost()
        logger.info(f"Token Usage: {self.total_input} input, {self.total_output} output")
        logger.info(f"Estimated Cost: ${cost:.4f}")

# Global tracker for current generation
_current_tracker: TokenTracker | None = None

async def _call_llm(system_prompt: str, user_content: str) -> str:
    """Helper function to call the Azure OpenAI API."""
    global _current_tracker
    
    response = await client.chat.completions.create(
        model=settings.AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )
    
    # Track tokens
    if response.usage and _current_tracker:
        _current_tracker.add(response.usage.prompt_tokens, response.usage.completion_tokens)
    
    return response.choices[0].message.content or ""


async def generate_notes_map_reduce(transcript_segments: list[dict]) -> tuple[str, dict]:
    """
    Map-Reduce generation for high-fidelity notes.
    
    1. Chunks the transcript.
    2. MAP: Processes each chunk independently.
    3. REDUCE: Synthesizes all chunk notes into a final document.
    
    Returns:
        tuple: (content_markdown, cost_stats)
        cost_stats = {"input_tokens": int, "output_tokens": int, "cost": float}
    """
    global _current_tracker
    _current_tracker = TokenTracker()
    
    try:
        # 1. Prepare full text from segments
        full_text = " ".join([s["text"] for s in transcript_segments])
        
        # 2. Chunk the text using the shared splitter
        chunks = text_splitter.split_text(full_text)
        
        logger.info(f"Map-Reduce: Processing {len(chunks)} chunks")
        
        # 3. MAP Phase: Process all chunks concurrently
        async def process_chunk(chunk_text: str, index: int) -> str:
            logger.info(f"Processing chunk {index + 1}/{len(chunks)}")
            prompt = MAP_PROMPT.format(text=chunk_text)
            return await _call_llm("You are a Senior Technical Writer.", prompt)
        
        map_tasks = [process_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        mapped_notes = await asyncio.gather(*map_tasks)
        
        # 4. REDUCE Phase: Combine all notes into final document
        # If too many chunks, we may need to reduce in batches
        combined_notes = "\n\n---\n\n".join(mapped_notes)
        
        # Check if combined notes are too long for a single reduce call
        if len(combined_notes) > 100000:
            # Do iterative reduction in batches of ~5 chunks at a time
            logger.info("Combined notes too long, doing iterative reduction")
            batch_size = 5
            while len(mapped_notes) > 1:
                new_mapped = []
                for i in range(0, len(mapped_notes), batch_size):
                    batch = mapped_notes[i:i+batch_size]
                    batch_text = "\n\n---\n\n".join(batch)
                    reduce_prompt = REDUCE_PROMPT.format(text=batch_text)
                    reduced = await _call_llm(
                        "You are a Senior Technical Editor.", 
                        reduce_prompt
                    )
                    new_mapped.append(reduced)
                mapped_notes = new_mapped
            _current_tracker.log_summary()
            return mapped_notes[0], _current_tracker.get_stats()
        else:
            # Single reduce pass
            reduce_prompt = REDUCE_PROMPT.format(text=combined_notes)
            result = await _call_llm(
                "You are a Senior Technical Editor.", 
                reduce_prompt
            )
            _current_tracker.log_summary()
            return result, _current_tracker.get_stats()
        
    except Exception as e:
        logger.error(f"Error generating map-reduce notes: {e}")
        return f"Error: {str(e)}", {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}
