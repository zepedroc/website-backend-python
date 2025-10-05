from typing import Optional

from agents import Agent, set_default_openai_client
from openai import AsyncOpenAI

from .settings import settings


_agent: Optional[Agent] = None


def get_agent() -> Agent:
    global _agent
    if _agent is not None:
        return _agent

    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Please create a .env file with your Groq API key. "
            "See .env.template for an example."
        )

    # Configure the custom OpenAI client
    async_client = AsyncOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )
    set_default_openai_client(async_client)

    _agent = Agent(
        name="Contact Draft Assistant",
        instructions="You are a helpful assistant that drafts short, professional messages for a portfolio website contact form. Keep messages friendly, concise, and on-topic.",
        model="llama-3.3-70b-versatile",
    )
    return _agent


