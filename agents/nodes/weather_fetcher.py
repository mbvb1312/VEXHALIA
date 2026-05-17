"""
Weather fetcher node — runs in parallel with the image fetcher.

This node calls the weather tool to get a 7-day forecast and stores
the structured data in the agent state. It runs concurrently with the
image fetcher node (Distinction Challenge #2: Parallel Fan-Out),
reducing overall latency since the two operations are independent.
"""

import asyncio

from agents.state import AgentState
from tools.weather_tool import get_weather


def weather_fetcher_node(state: AgentState) -> dict:
    """Fetch weather forecast for the city and update the state.

    We handle the async-to-sync bridge here because LangGraph nodes
    run synchronously by default. The actual API call inside get_weather
    is async for performance.
    """
    city = state.get("city_name", "")
    if not city:
        return {"weather_forecast": [], "error": "No city name for weather lookup"}

    try:
        loop = asyncio.new_event_loop()
        try:
            forecast_points = loop.run_until_complete(get_weather(city))
        finally:
            loop.close()

        # Convert Pydantic models to dicts for state serialization
        forecast_dicts = [point.model_dump() for point in forecast_points]
        return {"weather_forecast": forecast_dicts}

    except Exception as e:
        return {
            "weather_forecast": [],
            "error": f"Weather fetch failed: {str(e)}",
        }
