"""
Synthesizer node — the final node in the graph.

This node takes all the data collected by previous nodes (city summary,
weather forecast, images) and packages it into a structured TravelResponse
object. The Streamlit frontend parses this structured output to render
the UI components — it never sees raw markdown or unstructured text.
"""

from agents.state import AgentState
from models.schemas import TravelResponse, WeatherDataPoint, CityImage


def synthesizer_node(state: AgentState) -> dict:
    """Compose the final structured output from all collected data.

    This node validates that we have all the pieces and fills in
    sensible defaults for any missing components so the UI always
    has something to render.
    """
    city = state.get("city_name", "Unknown")
    summary = state.get("city_summary", "")
    weather_data = state.get("weather_forecast", [])
    image_urls = state.get("image_urls", [])
    images_raw = state.get("images", [])
    source = state.get("data_source", "unknown")

    # Build the weather forecast list — handle both dict and model forms
    forecast = []
    for item in weather_data:
        if isinstance(item, dict):
            forecast.append(WeatherDataPoint(**item))
        elif isinstance(item, WeatherDataPoint):
            forecast.append(item)

    # Build the images list
    images = []
    for item in images_raw:
        if isinstance(item, dict):
            images.append(CityImage(**item))
        elif isinstance(item, CityImage):
            images.append(item)

    # If we have no summary, provide a fallback message
    if not summary:
        summary = (
            f"We gathered information about {city} but could not generate "
            f"a detailed summary. Please check your LLM API key configuration."
        )

    # If we have images but not URLs (or vice versa), sync them
    if images and not image_urls:
        image_urls = [img.url for img in images]
    elif image_urls and not images:
        images = [CityImage(url=url, caption=f"View of {city}") for url in image_urls]

    # Build the final response object
    response = TravelResponse(
        city_name=city,
        city_summary=summary,
        weather_forecast=forecast,
        image_urls=image_urls,
        images=images,
        data_source=source,
    )

    # Store the serialized response in state for the UI to consume
    return {
        "city_summary": response.city_summary,
        "weather_forecast": [wp.model_dump() for wp in response.weather_forecast],
        "image_urls": response.image_urls,
        "images": [img.model_dump() for img in response.images],
        "data_source": response.data_source,
    }
