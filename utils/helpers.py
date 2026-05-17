"""
Shared utility functions used across the VEXHALIA application.

This module centralizes LLM instantiation so we only define the
provider-switching logic in one place. Every node that needs the LLM
calls get_llm() rather than constructing its own instance.
"""

from langchain_openai import ChatOpenAI
from config.settings import settings


_llm_instance = None


def get_llm() -> ChatOpenAI:
    """Return a configured LLM instance, cached after first creation.

    Uses the provider setting from config to decide between Groq (free)
    and OpenAI (paid). Both use the same ChatOpenAI class since Groq
    exposes an OpenAI-compatible endpoint — the only difference is the
    base URL and model name.
    """
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    cfg = settings.get_llm_config()

    kwargs = {
        "model": cfg["model"],
        "api_key": cfg["api_key"],
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    if cfg["base_url"]:
        kwargs["base_url"] = cfg["base_url"]

    _llm_instance = ChatOpenAI(**kwargs)
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
    - "Chennai"  (just the city name)
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

    Follow-up indicators:
    - "what about next week?"
    - "how about tomorrow?"
    - "update the weather"
    - Short messages that reference time but not a new city

    This supports Distinction Challenge #3 (Human-in-the-Loop with memory).
    """
    lower = user_input.lower().strip()
    follow_up_signals = [
        "next week", "this week", "tomorrow", "next month",
        "what about", "how about", "update", "refresh",
        "and the weather", "forecast for",
    ]
    return any(signal in lower for signal in follow_up_signals)
