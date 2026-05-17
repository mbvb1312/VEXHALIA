"""
Image fetcher node — runs in parallel with the weather fetcher.

This node retrieves city images and stores them in the agent state.
It runs concurrently with the weather fetcher node
(Distinction Challenge #2: Parallel Fan-Out).
"""

import asyncio

from agents.state import AgentState
from tools.image_tool import get_images


def image_fetcher_node(state: AgentState) -> dict:
    """Fetch images for the city and update the state.

    Similar to the weather fetcher, we bridge async to sync here.
    The image tool checks curated URLs for known cities and falls
    back to placeholder URLs for unknown ones.
    """
    city = state.get("city_name", "")
    if not city:
        return {"image_urls": [], "images": []}

    try:
        loop = asyncio.new_event_loop()
        try:
            image_objects = loop.run_until_complete(get_images(city))
        finally:
            loop.close()

        image_dicts = [img.model_dump() for img in image_objects]
        image_urls = [img.url for img in image_objects]

        return {
            "images": image_dicts,
            "image_urls": image_urls,
        }

    except Exception as e:
        return {
            "image_urls": [],
            "images": [],
            "error": f"Image fetch failed: {str(e)}",
        }
