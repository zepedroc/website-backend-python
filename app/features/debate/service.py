from typing import AsyncGenerator, Dict, Any
import httpx
import asyncio
from agents import Agent, Runner, set_default_openai_client
from openai import AsyncOpenAI
from bs4 import BeautifulSoup
import re

from ...settings import settings


async def scrape_webpage(url: str, max_length: int = 2000) -> str:
    """
    Scrape and extract main text content from a webpage.
    
    Args:
        url: The URL to scrape
        max_length: Maximum characters to return
        
    Returns:
        Cleaned text content or empty string on error
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                timeout=8.0
            )
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return text
            
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""


async def refine_search_query(topic: str) -> str:
    """
    Use an LLM agent to convert a debate topic into an optimized search query.
    
    Args:
        topic: The original debate topic
        
    Returns:
        A refined, search-engine-friendly query string
    """
    query_agent = Agent(
        name="Search Query Optimizer",
        instructions="You are an expert at creating effective search queries for Google.",
        model="llama-3.3-70b-versatile",
    )
    
    prompt = (
        f"Convert this debate topic into a concise Google search query (max 10 words) "
        f"that will find recent, relevant information:\n\n"
        f"Topic: {topic}\n\n"
        f"Respond with ONLY the search query, nothing else."
    )
    
    result = await Runner.run(query_agent, prompt)
    return (result.final_output or topic).strip()


async def perform_web_search(query: str) -> str:
    """
    Perform a web search using SerpAPI and scrape actual content from top results.
    
    Args:
        query: The search query
        
    Returns:
        Formatted string with actual web content or empty string on error
    """
    if not settings.SERPAPI_API_KEY:
        print("SERPAPI_API_KEY is not set")
        return ""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google",
                    "q": query,
                    "num": 5,
                    "api_key": settings.SERPAPI_API_KEY
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Get top URLs from organic results
            urls = []
            for item in data.get("organic_results", [])[:3]:  # Top 3 results
                link = item.get("link", "")
                title = item.get("title", "")
                if link and title:
                    urls.append((link, title))
            
            if not urls:
                print("No search results found")
                return ""
            
            # Scrape content from each URL
            results = []
            tasks = []
            titles = []
            for url, title in urls:
                print(f"Scraping: {title}")
                tasks.append(scrape_webpage(url))
                titles.append((url, title))

            contents = await asyncio.gather(*tasks, return_exceptions=True)

            for (url, title), content in zip(titles, contents):
                if isinstance(content, Exception):
                    print(f"Error scraping {url}: {content}")
                    continue
                if content:
                    results.append(f"📄 {title}\n{content}\nSource: {url}")
            
            if results:
                combined = "\n\n" + "="*80 + "\n\n"
                return combined.join(results)
            return ""
            
    except Exception as e:
        # Silently fail and return empty string if search fails
        print(f"Search error: {e}")
        return ""


async def generate_debate(topic: str, allow_search: bool = True) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Generate a debate between two AI agents with opposing positions on a given topic.
    
    Yields 6 messages total (3 from each debater) in alternating order.
    Each yielded dict contains: speaker, message, and position.
    
    Args:
        topic: The debate topic or question
        allow_search: Whether to enable web search for additional context (default: True)
        
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
        # instructions="You are an expert at identifying opposing viewpoints on any topic or question.",
        model="llama-3.3-70b-versatile",
    )
    
    position_prompt = (
        f"Given this topic or question: '{topic}'\n\n"
        "Decide the two sides of the debate and the position of the each side. Make it general, don't try to be specific about reasons"
        "Respond with ONLY the two sides of the debate, one per line:\n"
        "Side 1: [side 1]\n"
        "Side 2: [side 2]"
    )
    
    position_result = await Runner.run(position_agent, position_prompt)
    positions_text = (position_result.final_output or "").strip()
    
    # Parse positions
    lines = [line.strip() for line in positions_text.split("\n") if line.strip()]
    position_1 = lines[0].replace("Side 1:", "").strip() if len(lines) > 0 else "Supporting the topic"
    position_2 = lines[1].replace("Side 2:", "").strip() if len(lines) > 1 else "Opposing the topic"

    print("position_1: ", position_1)
    print("position_2: ", position_2)
    
    # Perform web search for additional context if enabled
    search_context = ""
    if allow_search:
        search_query = await refine_search_query(topic)
        search_results = await perform_web_search(search_query)
        
        # Format search context for debaters
        if search_results:
            search_context = (
                f"Background information from recent sources:\n\n"
                f"{search_results}\n\n"
            )
    
    # Create two debater agents with opposing positions
    debater_1 = Agent(
        name="Debater 1",
        instructions=(
            f"{search_context}"
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
            f"{search_context}"
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

