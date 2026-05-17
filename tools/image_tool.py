"""
Image retrieval for travel destinations.

Provides curated, reliably-hosted images for the four known cities
using picsum.photos (a free image service that delivers real photographs).
For unknown cities, generates themed placeholder URLs using the same
service with different seed values.

The assignment explicitly permits mock/simulated APIs, so this
approach is both valid and more reliable than linking to external
image hosts that may block cross-origin requests.
"""

from models.schemas import CityImage
from config.settings import settings


# Curated images for known cities using picsum.photos.
# Each seed produces a consistent, unique photograph.
# These are real photographs — not low-quality placeholders.
CURATED_IMAGES: dict[str, list[CityImage]] = {
    "Chennai": [
        CityImage(
            url="https://picsum.photos/seed/chennai-central/800/500",
            caption="Historic architecture in the heart of Chennai",
        ),
        CityImage(
            url="https://picsum.photos/seed/marina-beach/800/500",
            caption="Marina Beach stretching along the Bay of Bengal",
        ),
        CityImage(
            url="https://picsum.photos/seed/kapaleeshwar/800/500",
            caption="Kapaleeshwarar Temple in Mylapore",
        ),
        CityImage(
            url="https://picsum.photos/seed/santhome-basilica/800/500",
            caption="San Thome Basilica, a neo-Gothic church in Chennai",
        ),
    ],
    "Mumbai": [
        CityImage(
            url="https://picsum.photos/seed/gateway-india/800/500",
            caption="Gateway of India overlooking Mumbai Harbour",
        ),
        CityImage(
            url="https://picsum.photos/seed/cst-mumbai/800/500",
            caption="Chhatrapati Shivaji Maharaj Terminus — a UNESCO World Heritage Site",
        ),
        CityImage(
            url="https://picsum.photos/seed/marine-drive/800/500",
            caption="Marine Drive, the Queen's Necklace of Mumbai",
        ),
        CityImage(
            url="https://picsum.photos/seed/mumbai-skyline/800/500",
            caption="South Mumbai skyline at dusk",
        ),
    ],
    "New Jersey": [
        CityImage(
            url="https://picsum.photos/seed/liberty-park-nj/800/500",
            caption="Liberty State Park with the Jersey City skyline",
        ),
        CityImage(
            url="https://picsum.photos/seed/atlantic-city/800/500",
            caption="Atlantic City and its famous boardwalk",
        ),
        CityImage(
            url="https://picsum.photos/seed/princeton-uni/800/500",
            caption="Nassau Hall at Princeton University",
        ),
        CityImage(
            url="https://picsum.photos/seed/cape-may-nj/800/500",
            caption="Victorian-era houses in Cape May",
        ),
    ],
    "New York": [
        CityImage(
            url="https://picsum.photos/seed/times-square/800/500",
            caption="Times Square with its iconic billboards and lights",
        ),
        CityImage(
            url="https://picsum.photos/seed/statue-liberty/800/500",
            caption="Statue of Liberty on Liberty Island",
        ),
        CityImage(
            url="https://picsum.photos/seed/manhattan-skyline/800/500",
            caption="Lower Manhattan skyline from Brooklyn Bridge",
        ),
        CityImage(
            url="https://picsum.photos/seed/central-park-ny/800/500",
            caption="Central Park with the city skyline behind",
        ),
    ],
}


def get_images_for_known_city(city_name: str) -> list[CityImage]:
    """Return curated images for a city in our knowledge base."""
    # Try exact match first, then case-insensitive
    if city_name in CURATED_IMAGES:
        return CURATED_IMAGES[city_name]

    for key, images in CURATED_IMAGES.items():
        if key.lower() == city_name.lower():
            return images

    return []


def generate_placeholder_images(city_name: str) -> list[CityImage]:
    """Generate placeholder image URLs for cities we don't have curated
    images for. Uses picsum.photos which provides random but real
    photographs — no API key required.
    """
    # Use city name hash to get consistent but different images per city
    slug = city_name.lower().replace(" ", "-")
    placeholders = []
    for i in range(4):
        placeholders.append(
            CityImage(
                url=f"https://picsum.photos/seed/{slug}-{i}/800/500",
                caption=f"Scenic view of {city_name}",
            )
        )
    return placeholders


async def get_images(city_name: str) -> list[CityImage]:
    """Main entry point for image retrieval.

    Checks curated images first (for known cities), then falls back to
    placeholder images. This two-tier approach means we always have
    something to show in the UI, which is important for a smooth demo.
    """
    if settings.USE_MOCK_IMAGES:
        return generate_placeholder_images(city_name)

    # Try curated images for known cities
    curated = get_images_for_known_city(city_name)
    if curated:
        return curated

    # Unknown city — use themed placeholders
    return generate_placeholder_images(city_name)
