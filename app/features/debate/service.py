from typing import AsyncGenerator, Dict, Any
from agents import Agent, Runner, set_default_openai_client
from openai import AsyncOpenAI

from ...settings import settings


async def generate_debate(topic: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Generate a debate between two AI agents with opposing positions on a given topic.
    
    Yields 6 messages total (3 from each debater) in alternating order.
    Each yielded dict contains: speaker, message, and position.
    
    Args:
        topic: The debate topic or question
        
    Yields:
        Dict with keys: speaker (str), message (str), position (str)
    """
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
    
    # Configure the OpenAI client
    async_client = AsyncOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )
    set_default_openai_client(async_client)
    
    # Determine the two opposing positions from the topic
    position_agent = Agent(
        name="Position Analyzer",
        instructions="You are an expert at identifying opposing viewpoints on any topic or question.",
        model="llama-3.3-70b-versatile",
    )
    
    position_prompt = (
        f"Given this topic or question: '{topic}'\n\n"
        "Identify two clear, opposing positions that could be debated. "
        "Respond with ONLY two brief position statements (max 10 words each), one per line:\n"
        "Position 1: [brief statement]\n"
        "Position 2: [brief statement]"
    )
    
    position_result = await Runner.run(position_agent, position_prompt)
    positions_text = (position_result.final_output or "").strip()
    
    # Parse positions
    lines = [line.strip() for line in positions_text.split("\n") if line.strip()]
    position_1 = lines[0].replace("Position 1:", "").strip() if len(lines) > 0 else "Supporting the topic"
    position_2 = lines[1].replace("Position 2:", "").strip() if len(lines) > 1 else "Opposing the topic"
    
    # Create two debater agents with opposing positions
    debater_1 = Agent(
        name="Debater 1",
        instructions=(
            f"You're chatting as a friend who leans toward: {position_1}.\n"
            f"Topic: {topic}\n\n"
            "Style guidelines (casual chat, not a courtroom):\n"
            "- Sound natural and friendly; use contractions (you're, it's, don't).\n"
            "- Keep it short (1–2 sentences), conversational, no lists or bullet points.\n"
            "- Build on what the other person just said; acknowledge good points.\n"
            "- Ask an occasional brief question to keep it flowing.\n"
            "- Avoid formal debate language, citations, or jargon.\n"
            "- No role-play meta talk (don't say 'as an AI' or 'as a debater')."
        ),
        model="llama-3.3-70b-versatile",
    )
    
    debater_2 = Agent(
        name="Debater 2",
        instructions=(
            f"You're chatting as a friend who leans toward: {position_2}.\n"
            f"Topic: {topic}\n\n"
            "Style guidelines (casual chat, not a courtroom):\n"
            "- Sound natural and friendly; use contractions (you're, it's, don't).\n"
            "- Keep it short (1–2 sentences), conversational, no lists or bullet points.\n"
            "- Build on what the other person just said; acknowledge good points.\n"
            "- Ask an occasional brief question to keep it flowing.\n"
            "- Avoid formal debate language, citations, or jargon.\n"
            "- No role-play meta talk (don't say 'as an AI' or 'as a debater')."
        ),
        model="llama-3.3-70b-versatile",
    )
    
    # Store conversation history
    conversation_history = []
    
    # Generate 6 messages (3 from each debater)
    for turn in range(6):
        # Alternate between debaters
        is_debater_1 = (turn % 2 == 0)
        current_agent = debater_1 if is_debater_1 else debater_2
        current_speaker = "debater_1" if is_debater_1 else "debater_2"
        current_position = position_1 if is_debater_1 else position_2
        
        # Build the prompt with conversation history
        if turn == 0:
            # First message - opening note (friendly, informal)
            prompt = (
                f"Start a casual conversation with a greeting, then bring up: {topic}. "
                "Say hello naturally, then share your take in 1–2 sentences total. Keep it light and conversational."
            )
        else:
            # Subsequent messages - respond to the debate
            prompt = (
                f"Continue the casual chat about: {topic}\n\n"
                "Conversation so far (most recent last):\n"
            )
            for i, msg in enumerate(conversation_history):
                speaker_label = "Your opponent" if msg["speaker"] != current_speaker else "You"
                prompt += f"{speaker_label}: {msg['message']}\n\n"
            
            prompt += (
                "Reply like a friend: acknowledge what was said, add your perspective, "
                "maybe ask a short follow-up. Keep it 1–2 sentences, no lists."
            )

            # Final turn: close the conversation without a question
            if turn == 5:
                prompt += (
                    " This is your last message. Wrap up warmly and end with a concise "
                    "statement (no questions)."
                )
        
        # Generate the message
        result = await Runner.run(current_agent, prompt)
        message = (result.final_output or "").strip()
        
        # Store in history
        message_data = {
            "speaker": current_speaker,
            "message": message,
            "position": current_position
        }
        conversation_history.append(message_data)
        
        # Yield the message
        yield message_data

