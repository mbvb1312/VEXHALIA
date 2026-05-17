"""
Pydantic schemas for structured data flowing through the agent graph.

Every node in the LangGraph pipeline produces or consumes these models,
ensuring type safety and making the final output parseable by Streamlit
without guesswork.
"""

from __future__ import annotations
from pydantic import BaseModel, Field


class WeatherDataPoint(BaseModel):
    """A single day's weather forecast data.

    Fields are chosen to match what Open-Meteo returns after parsing,
    and what looks good on a Plotly line chart.
    """

    date: str = Field(description="ISO date string, e.g. 2026-05-18")
    temperature_high: float = Field(description="Daily max temperature in Celsius")
    temperature_low: float = Field(description="Daily min temperature in Celsius")
    humidity: float = Field(default=0.0, description="Relative humidity percentage")
    precipitation_chance: float = Field(
        default=0.0, description="Precipitation probability as percentage"
    )
    condition: str = Field(
        default="Clear", description="Human-readable weather condition"
    )


class CityImage(BaseModel):
    """Metadata for a single image of the destination."""

    url: str = Field(description="Direct URL to the image")
    caption: str = Field(default="", description="Short description of the image")


class TravelResponse(BaseModel):
    """The structured output that the synthesizer node produces.

    This is the contract between the agent backend and the Streamlit
    frontend — the UI parses exactly this shape.
    """

    city_name: str = Field(description="Canonical name of the city")
    city_summary: str = Field(
        description="Rich text summary of the city's highlights"
    )
    weather_forecast: list[WeatherDataPoint] = Field(
        default_factory=list,
        description="5-7 day forecast data points for charting",
    )
    image_urls: list[str] = Field(
        default_factory=list,
        description="URLs of high-quality city images",
    )
    images: list[CityImage] = Field(
        default_factory=list,
        description="Structured image objects with captions",
    )
    data_source: str = Field(
        default="unknown",
        description="Where the city info came from: 'vector_store' or 'web_search'",
    )
