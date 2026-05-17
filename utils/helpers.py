"""
Shared utility functions used across the VEXHALIA application.

This module centralizes LLM instantiation so we only define the
provider-switching logic in one place. Every node that needs the LLM
calls get_llm() rather than constructing its own instance.
"""

from langchain_openai import ChatOpenAI
from config.settings import settings


_llm_instance = None


def _build_groq_fallback():
    """Build a Groq LLM instance for use as a fallback provider.

    Groq is free-tier and has generous rate limits, making it an
    ideal backup when Gemini's per-hour quota is exhausted.
    """
    return ChatOpenAI(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        base_url=settings.GROQ_BASE_URL,
        temperature=0.7,
        max_tokens=1024,
    )


def get_llm():
    """Return a configured LLM instance with automatic fallback.

    Provider priority: Gemini → Groq (automatic failover).

    When Gemini is the primary provider, Groq is chained as a
    fallback using LangChain's with_fallbacks(). If Gemini hits
    its rate limit (free tier: limited requests/hour), the system
    seamlessly switches to Groq without any user-visible error.

    This ensures 24/7 availability even under heavy usage.
    """
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    cfg = settings.get_llm_config()
    provider = cfg.get("provider", "groq")

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        primary = ChatGoogleGenerativeAI(
            model=cfg["model"],
            google_api_key=cfg["api_key"],
            temperature=0.7,
            max_output_tokens=2048,
        )
        # Chain Groq as automatic fallback for rate-limit resilience
        if settings.GROQ_API_KEY:
            fallback = _build_groq_fallback()
            _llm_instance = primary.with_fallbacks([fallback])
        else:
            _llm_instance = primary

    elif provider == "openai":
        primary = ChatOpenAI(
            model=cfg["model"],
            api_key=cfg["api_key"],
            temperature=0.7,
            max_tokens=2048,
        )
        # Chain Groq as fallback for OpenAI too
        if settings.GROQ_API_KEY:
            fallback = _build_groq_fallback()
            _llm_instance = primary.with_fallbacks([fallback])
        else:
            _llm_instance = primary

    else:
        # Groq is already the cheapest option — no fallback needed
        _llm_instance = _build_groq_fallback()

    return _llm_instance


def reset_llm():
    """Force re-creation of the LLM instance.

    Useful when settings change at runtime (e.g., user provides a
    different API key through the Streamlit sidebar).
    """
    global _llm_instance
    _llm_instance = None


def extract_city_name(user_input: str) -> str:
    """Extract a plausible city name from the user's input.

    This handles common patterns like:
    - "Tell me about Kyoto"
    - "What's Tokyo like?"
    - "Paris"  (just the city name)
    - "I want to visit Mumbai next week"

    For ambiguous inputs, we return the cleaned-up input and let the
    router figure out if it is in the vector store.
    """
    # Remove common preamble phrases
    removals = [
        "tell me about", "what about", "show me", "i want to visit",
        "i want to go to", "what's", "what is", "how about",
        "let's explore", "explore", "search for", "find",
        "information on", "info about", "info on",
    ]
    cleaned = user_input.strip()
    lower = cleaned.lower()

    for phrase in removals:
        if lower.startswith(phrase):
            cleaned = cleaned[len(phrase):].strip()
            lower = cleaned.lower()

    # Remove trailing question marks, periods, etc.
    cleaned = cleaned.rstrip("?.!,")

    # Remove time-related suffixes (for follow-up detection)
    time_words = ["next week", "this week", "tomorrow", "today", "next month"]
    for tw in time_words:
        if cleaned.lower().endswith(tw):
            cleaned = cleaned[: -len(tw)].strip()

    # Capitalize properly
    if cleaned:
        cleaned = cleaned.strip()
        # Title-case the city name
        cleaned = " ".join(word.capitalize() for word in cleaned.split())

    return cleaned


def is_follow_up_query(user_input: str) -> bool:
    """Detect if the user's message is a follow-up rather than a new query.

    Follow-up indicators include time references, activity questions about
    a previously mentioned city, and weather update requests. This supports
    Distinction Challenge #3 (Human-in-the-Loop with memory).
    """
    lower = user_input.lower().strip()
    follow_up_signals = [
        "next week", "this week", "tomorrow", "next month", "yesterday",
        "what about", "how about", "update", "refresh",
        "and the weather", "forecast for", "next 7 days", "next 5 days",
        "will it rain", "will it be", "is it good", "should i",
        "can i go", "boating", "hiking", "outdoor", "weekend",
        "previous day", "last week", "today's weather",
    ]
    return any(signal in lower for signal in follow_up_signals)
