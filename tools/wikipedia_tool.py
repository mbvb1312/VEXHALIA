"""
Wikipedia integration for enriched city information.

Fetches structured summary data from Wikipedia to supplement
the vector store and web search results. This gives the LLM
richer factual context to synthesize travel summaries from.

The wikipedia package handles API rate limits and disambiguation
internally, so we only need simple error handling here.
"""

import wikipedia


def get_wikipedia_summary(city_name: str, sentences: int = 8) -> str:
    """Fetch a Wikipedia summary for the given city.

    Parameters:
        city_name: Name of the city to look up.
        sentences: Number of sentences to retrieve (Wikipedia truncates
                   at this count for the summary endpoint).

    Returns:
        A text summary from Wikipedia, or an empty string if the
        lookup fails (disambiguation, network error, etc.).
    """
    try:
        # Search for the most relevant page
        search_results = wikipedia.search(f"{city_name} city", results=3)
        if not search_results:
            return ""

        # Try each result until we find a valid page
        for result in search_results:
            try:
                summary = wikipedia.summary(result, sentences=sentences)
                # Verify this is actually about the right place
                if city_name.lower() in summary.lower():
                    return summary
            except wikipedia.DisambiguationError as e:
                # Pick the first option from disambiguation
                if e.options:
                    try:
                        return wikipedia.summary(e.options[0], sentences=sentences)
                    except Exception:
                        continue
            except wikipedia.PageError:
                continue

        # Fallback: just use the first search result
        return wikipedia.summary(search_results[0], sentences=sentences)

    except Exception:
        # Network error, rate limit, etc. — return empty
        return ""


def get_wikipedia_sections(city_name: str) -> dict[str, str]:
    """Fetch key sections from a city's Wikipedia page.

    Returns a dict mapping section titles to their content.
    Useful for extracting specific info like 'Geography', 'Culture',
    'Tourism', etc.
    """
    try:
        page = wikipedia.page(f"{city_name} city")
        # Return the full content — the LLM will extract what it needs
        return {
            "title": page.title,
            "summary": page.summary,
            "url": page.url,
        }
    except Exception:
        return {}
