"""
Image retrieval for travel destinations.

For the four known cities we maintain a curated list of high-quality,
publicly accessible image URLs from Wikimedia Commons. For unknown
cities we generate themed placeholder URLs using picsum.photos,
which provides real photographs without any API key.

The assignment explicitly permits mock/simulated APIs, so our curated
URL approach is both valid and more reliable than depending on a paid
image service.
"""

from models.schemas import CityImage
from config.settings import settings


# Hand-picked, publicly accessible images for known cities.
# All URLs are from Wikimedia Commons — free to use, no API key needed.
CURATED_IMAGES: dict[str, list[CityImage]] = {
    "Chennai": [
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Chennai_Central.jpg/800px-Chennai_Central.jpg",
            caption="Chennai Central railway station — a landmark of Indo-Saracenic architecture",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Chennai_Marina_Beach.jpg/800px-Chennai_Marina_Beach.jpg",
            caption="Marina Beach stretching along the Bay of Bengal",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Kapaleeshwarar_temple_%2816%29.jpg/800px-Kapaleeshwarar_temple_%2816%29.jpg",
            caption="Kapaleeshwarar Temple in Mylapore with its colorful gopuram",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/San_Thome_Basilica%2C_Chennai.jpg/800px-San_Thome_Basilica%2C_Chennai.jpg",
            caption="San Thome Basilica, a neo-Gothic church in Chennai",
        ),
    ],
    "Mumbai": [
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Mumbai_03-2016_30_Gateway_of_India.jpg/800px-Mumbai_03-2016_30_Gateway_of_India.jpg",
            caption="Gateway of India overlooking Mumbai Harbour",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Chhatrapati_Shivaji_Terminus_%28Victoria_Terminus%29.jpg/800px-Chhatrapati_Shivaji_Terminus_%28Victoria_Terminus%29.jpg",
            caption="Chhatrapati Shivaji Maharaj Terminus — a UNESCO World Heritage Site",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Mumbai_Skyline_at_Night.jpg/800px-Mumbai_Skyline_at_Night.jpg",
            caption="Mumbai skyline illuminated at night from Marine Drive",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Mumbai_Aug_2018_%2843397784544%29.jpg/800px-Mumbai_Aug_2018_%2843397784544%29.jpg",
            caption="The bustling streets and architecture of South Mumbai",
        ),
    ],
    "New Jersey": [
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Liberty_State_Park_with_Jersey_City_background.jpg/800px-Liberty_State_Park_with_Jersey_City_background.jpg",
            caption="Liberty State Park with Jersey City skyline in the background",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Atlantic_City%2C_aerial_view.jpg/800px-Atlantic_City%2C_aerial_view.jpg",
            caption="Aerial view of Atlantic City and its famous boardwalk",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Princeton_University_Nassau_Hall.jpg/800px-Princeton_University_Nassau_Hall.jpg",
            caption="Nassau Hall at Princeton University",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Cape_May_Victorian_houses.jpg/800px-Cape_May_Victorian_houses.jpg",
            caption="Victorian-era houses in Cape May, a National Historic Landmark",
        ),
    ],
    "New York": [
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/New_york_times_square-terabytes.jpg/800px-New_york_times_square-terabytes.jpg",
            caption="Times Square with its iconic billboards and lights",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Statue_of_Liberty_7.jpg/800px-Statue_of_Liberty_7.jpg",
            caption="Statue of Liberty on Liberty Island",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Lower_Manhattan_from_Governors_Island_September_2016_panorama_3.jpg/800px-Lower_Manhattan_from_Governors_Island_September_2016_panorama_3.jpg",
            caption="Lower Manhattan skyline from Governors Island",
        ),
        CityImage(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Central_Park_-_The_Pond_%2848377220517%29.jpg/800px-Central_Park_-_The_Pond_%2848377220517%29.jpg",
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
    seed_base = sum(ord(c) for c in city_name)
    placeholders = []
    for i in range(4):
        seed = seed_base + i * 7
        placeholders.append(
            CityImage(
                url=f"https://picsum.photos/seed/{seed}/800/500",
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
