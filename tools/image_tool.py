"""
Image retrieval for travel destinations using real web search.

Instead of serving random placeholder photos, this module queries
DuckDuckGo Images to find actual photographs of the city's landmarks,
skyline, and tourist attractions. The results are real, publicly-hosted
images that match the destination being explored.

Fallback: If the image search fails (rate limits, network issues), we
return a small set of seeded placeholders so the UI never breaks.
"""

from ddgs import DDGS
from models.schemas import CityImage
from config.settings import settings


def search_city_images(city_name: str, max_results: int = 6) -> list[CityImage]:
    """Search the web for real photographs of a city.

    Uses DuckDuckGo image search to find actual photos of landmarks,
    skylines, and popular attractions. The keywords are crafted to
    prioritize high-quality travel photography over clip-art or logos.
    """
    # Queries designed to return travel photography, not random content.
    # Adding explicit 'tourist' or 'travel' terms helps DuckDuckGo rank
    # relevant images higher than unrelated results.
    queries = [
        f"{city_name} tourist attractions places to visit",
        f"{city_name} travel destination skyline scenery",
    ]

    collected = []
    seen_urls = set()

    try:
        ddgs = DDGS()
        for query in queries:
            if len(collected) >= max_results:
                break

            results = list(ddgs.images(
                query,
                max_results=max_results + 4,  # fetch extra so we can filter
            ))

            for img in results:
                url = img.get("image", "")
                title = img.get("title", f"View of {city_name}")

                # Skip duplicate URLs or tiny thumbnails
                if not url or url in seen_urls:
                    continue
                if any(bad in url.lower() for bad in ["logo", "icon", "avatar", ".svg"]):
                    continue

                seen_urls.add(url)
                collected.append(CityImage(url=url, caption=title))

                if len(collected) >= max_results:
                    break

    except Exception:
        # Rate limited or network error — fall through to fallback below
        pass

    return collected


def generate_fallback_images(city_name: str) -> list[CityImage]:
    """Return themed placeholder URLs when live image search is unavailable.

    Uses picsum.photos with city-derived seeds so each city gets consistent
    (though generic) images across sessions.
    """
    slug = city_name.lower().replace(" ", "-")
    return [
        CityImage(
            url=f"https://picsum.photos/seed/{slug}-{i}/800/500",
            caption=f"Scenic view of {city_name}",
        )
        for i in range(4)
    ]


async def get_images(city_name: str) -> list[CityImage]:
    """Main entry point for image retrieval.

    Attempts a live DuckDuckGo image search first. If that returns
    nothing (network issues, rate limits), falls back to generic
    placeholder images so the UI always renders something.
    """
    if settings.USE_MOCK_IMAGES:
        return generate_fallback_images(city_name)

    images = search_city_images(city_name)
    if images:
        return images

    # Live search returned nothing — use fallback
    return generate_fallback_images(city_name)
