"""
Configuration management for the VEXHALIA travel assistant.

Loads environment variables and provides a single Settings object
that the rest of the application imports. This keeps all magic strings
and default values in one place instead of scattered across modules.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Centralized application settings loaded from environment variables."""

    # ---- LLM Configuration ----
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()

    # Google Gemini (free tier — best quality)
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Groq (free fallback)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # OpenAI (paid — premium option)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o"

    # ---- Feature Flags ----
    USE_MOCK_WEATHER: bool = os.getenv("USE_MOCK_WEATHER", "false").lower() == "true"
    USE_MOCK_IMAGES: bool = os.getenv("USE_MOCK_IMAGES", "false").lower() == "true"
    USE_MOCK_SEARCH: bool = os.getenv("USE_MOCK_SEARCH", "false").lower() == "true"

    # ---- Vector Store ----
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    CHROMA_COLLECTION: str = "city_knowledge"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # The similarity threshold below which we consider a city "unknown"
    # and fall back to web search. Lower means stricter matching.
    SIMILARITY_THRESHOLD: float = 0.55

    # ---- Weather API (Open-Meteo, no key required) ----
    WEATHER_API_BASE: str = "https://api.open-meteo.com/v1"
    GEOCODING_API_BASE: str = "https://geocoding-api.open-meteo.com/v1"
    FORECAST_DAYS: int = 16  # Open-Meteo max is 16 days

    # ---- Known Cities for Vector Store ----
    KNOWN_CITIES: list[str] = ["Paris", "Tokyo", "New York"]

    @classmethod
    def get_llm_config(cls) -> dict:
        """Return the appropriate LLM configuration based on provider choice.

        Priority: gemini → openai → groq (fallback)
        """
        if cls.LLM_PROVIDER == "gemini" and cls.GOOGLE_API_KEY:
            return {
                "provider": "gemini",
                "api_key": cls.GOOGLE_API_KEY,
                "model": cls.GEMINI_MODEL,
                "base_url": None,
            }
        if cls.LLM_PROVIDER == "openai" and cls.OPENAI_API_KEY:
            return {
                "provider": "openai",
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.OPENAI_MODEL,
                "base_url": None,
            }
        # Default to Groq (free tier)
        return {
            "provider": "groq",
            "api_key": cls.GROQ_API_KEY,
            "model": cls.GROQ_MODEL,
            "base_url": cls.GROQ_BASE_URL,
        }

    @classmethod
    def validate(cls) -> list[str]:
        """Check that minimum required configuration is present.
        Returns a list of warning messages (empty if everything is fine).
        """
        warnings = []
        llm_cfg = cls.get_llm_config()
        if not llm_cfg["api_key"]:
            warnings.append(
                "No LLM API key found. Set GOOGLE_API_KEY, GROQ_API_KEY, "
                "or OPENAI_API_KEY in your .env file."
            )
        return warnings


settings = Settings()
