"""
LangGraph state definition for the travel assistant agent.

This TypedDict is the single source of truth that flows through every
node in the graph. Each node reads what it needs and writes back its
results. Using Annotated with add_messages lets LangGraph handle
message list merging automatically when nodes run in parallel.
"""

from __future__ import annotations
from typing import Annotated, TypedDict

from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

from models.schemas import WeatherDataPoint, CityImage


class AgentState(TypedDict):
    """The state object passed between all nodes in the LangGraph.

    Attributes:
        messages: Chat message history (LLM + tool messages).
                  Uses add_messages reducer for automatic merging.
        city_name: The city the user asked about (extracted from input).
        city_summary: Synthesized text about the city.
        weather_forecast: List of daily forecast data points.
        image_urls: Flat list of image URLs for the UI.
        images: Structured image objects with captions.
        data_source: Whether info came from 'vector_store' or 'web_search'.
        is_follow_up: True if this query builds on a previous one
                      (e.g., 'what about next week?' after asking about Tokyo).
        error: Error message if something went wrong, None otherwise.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    city_name: str
    city_summary: str
    weather_forecast: list[dict]
    image_urls: list[str]
    images: list[dict]
    data_source: str
    is_follow_up: bool
    error: str | None
