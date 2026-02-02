from openai import AsyncAzureOpenAI
from app.config import settings
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = AsyncAzureOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
)

SYSTEM_PROMPT = """You are a Senior Technical Writer. Convert the following transcript into clean, structured Markdown notes.

Rules:
- Output pure Markdown only. No explanations outside Markdown.
- Use '###' for sub-section headers based on topic shifts.
- Preserve any described code into proper Markdown code blocks with language tags (e.g., ```python).
- Preserve mathematical expressions as formulas.
- Use bullet points for step-by-step processes.
- Bold important terms and concepts.
- Remove conversational filler (e.g., 'in this video', 'the speaker says').
- Focus strictly on the technical content: what is being explained and how it works.
- Include a Title and a Table of Contents at the top.
"""


async def generate_technical_notes(transcript: str) -> str:
    """
    Sends the transcript to Azure OpenAI to generate technical notes.
    """
    try:
        # Simple token count estimation (4 chars ~= 1 token).
        # GPT-4o has 128k context. Safe limit approx 120k tokens -> ~480k chars.
        if len(transcript) > 400000:
            logger.warning(
                "Transcript is very long, truncating to 400k chars for safety."
            )
            transcript = transcript[:400000]

        response = await client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is the transcript:\n\n{transcript}"},
            ],
            temperature=0.2,  # Low temperature for factual accuracy
        )

        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating notes: {e}")
        # In a real app, might want to raise HTTPException, but returning error string is safer for now to avoid crash loop
        raise e
