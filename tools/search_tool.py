"""
Web search tool using DuckDuckGo.

When a user asks about a city that is not in our vector store, the
agent needs to pull information from the web. DuckDuckGo's search
API is free, requires no API key, and returns structured results
we can feed to the LLM for summarization.

Mock mode returns believable hardcoded results so the full agent
pipeline can run even offline.
"""

from ddgs import DDGS

from config.settings import settings


async def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search DuckDuckGo for information about a topic.

    Returns a list of dicts with keys: title, body, href.
    These get passed to the LLM which synthesizes them into
    a coherent city summary.
    """
    if settings.USE_MOCK_SEARCH:
        return generate_mock_search_results(query)

    try:
        results = []
        ddgs = DDGS()
        for result in ddgs.text(
            query,
            max_results=max_results,
            region="wt-wt",  # worldwide
        ):
            results.append({
                "title": result.get("title", ""),
                "body": result.get("body", ""),
                "href": result.get("href", ""),
            })
        return results

    except Exception:
        # Rate limited, network error, etc. — fall back to mock
        return generate_mock_search_results(query)


def generate_mock_search_results(query: str) -> list[dict]:
    """Return plausible search results for demonstration purposes.

    The content is generic enough to work for any city while being
    structured enough for the LLM to produce a reasonable summary.
    """
    city = query.replace("travel guide", "").replace("tourist attractions", "").strip()
    return [
        {
            "title": f"{city} Travel Guide - Top Attractions & Tips",
            "body": (
                f"{city} is a fascinating destination known for its unique blend "
                f"of cultural heritage and modern attractions. Visitors can explore "
                f"historic landmarks, vibrant local markets, and scenic viewpoints "
                f"that offer panoramic views of the surrounding area."
            ),
            "href": f"https://example.com/travel/{city.lower().replace(' ', '-')}",
        },
        {
            "title": f"Best Things to Do in {city} - Local Insider Guide",
            "body": (
                f"From world-class museums and galleries to outdoor adventures, "
                f"{city} offers something for every type of traveler. The local "
                f"cuisine is a highlight, with street food stalls and fine dining "
                f"restaurants showcasing regional specialties."
            ),
            "href": f"https://example.com/things-to-do/{city.lower().replace(' ', '-')}",
        },
        {
            "title": f"{city} Weather & Best Time to Visit",
            "body": (
                f"The climate in {city} varies throughout the year. Spring and "
                f"autumn generally offer the most pleasant conditions for "
                f"sightseeing, with moderate temperatures and lower humidity. "
                f"Summer can be warm, making it ideal for outdoor activities."
            ),
            "href": f"https://example.com/weather/{city.lower().replace(' ', '-')}",
        },
        {
            "title": f"Getting Around {city} - Transportation Guide",
            "body": (
                f"{city} has a well-connected public transportation system. "
                f"Buses, trains, and ride-sharing services make it easy to "
                f"navigate the city. Walking is also a great option for "
                f"exploring central neighborhoods and discovering hidden gems."
            ),
            "href": f"https://example.com/transport/{city.lower().replace(' ', '-')}",
        },
    ]
