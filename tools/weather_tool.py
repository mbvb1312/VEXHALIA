"""
Weather data fetching via the Open-Meteo API.

Open-Meteo is completely free, requires no API key, and provides
hourly and daily forecasts up to 16 days out. We use their geocoding
endpoint to convert city names to coordinates, then fetch the daily
forecast.

If the live API is unavailable or mock mode is enabled, we return
realistic hardcoded data so the agent's processing logic can still
be demonstrated end-to-end.
"""

import httpx
from datetime import datetime, timedelta

from config.settings import settings
from models.schemas import WeatherDataPoint


# WMO weather interpretation codes → human-readable conditions
# Reference: https://open-meteo.com/en/docs
WMO_CODE_MAP: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


async def geocode_city(city_name: str) -> tuple[float, float] | None:
    """Convert a city name to latitude/longitude using Open-Meteo geocoding.

    Returns None if the city cannot be found, which triggers mock data
    as a fallback rather than crashing the pipeline.
    """
    url = f"{settings.GEOCODING_API_BASE}/search"
    params = {"name": city_name, "count": 1, "language": "en", "format": "json"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        return None

    location = data["results"][0]
    return location["latitude"], location["longitude"]


async def fetch_weather_live(city_name: str) -> list[WeatherDataPoint]:
    """Fetch a 7-day daily forecast from Open-Meteo for the given city.

    The pipeline:
    1. Geocode city name → lat/lon
    2. Request daily forecast variables
    3. Parse WMO weather codes into readable conditions
    4. Return structured WeatherDataPoint objects
    """
    coords = await geocode_city(city_name)
    if coords is None:
        # City not found in geocoding — use mock data
        return generate_mock_weather(city_name)

    lat, lon = coords
    url = f"{settings.WEATHER_API_BASE}/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": (
            "temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,"
            "relative_humidity_2m_max,"
            "weather_code"
        ),
        "timezone": "auto",
        "forecast_days": settings.FORECAST_DAYS,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    temp_highs = daily.get("temperature_2m_max", [])
    temp_lows = daily.get("temperature_2m_min", [])
    precip_chances = daily.get("precipitation_probability_max", [])
    humidities = daily.get("relative_humidity_2m_max", [])
    weather_codes = daily.get("weather_code", [])

    forecast = []
    for i in range(len(dates)):
        wmo_code = weather_codes[i] if i < len(weather_codes) else 0
        condition = WMO_CODE_MAP.get(wmo_code, "Unknown")

        point = WeatherDataPoint(
            date=dates[i],
            temperature_high=temp_highs[i] if i < len(temp_highs) else 20.0,
            temperature_low=temp_lows[i] if i < len(temp_lows) else 10.0,
            humidity=humidities[i] if i < len(humidities) else 50.0,
            precipitation_chance=precip_chances[i] if i < len(precip_chances) else 0.0,
            condition=condition,
        )
        forecast.append(point)

    return forecast


def generate_mock_weather(city_name: str) -> list[WeatherDataPoint]:
    """Produce realistic-looking mock weather data for demonstration.

    The mock data uses a base temperature that varies by city name
    hash so different cities get different-looking forecasts, making
    demos more convincing.
    """
    # Use city name to seed slightly different base temperatures
    base_temp = 18.0 + (sum(ord(c) for c in city_name) % 15)
    today = datetime.now()

    mock_conditions = [
        "Clear sky", "Partly cloudy", "Mainly clear",
        "Slight rain", "Partly cloudy", "Clear sky", "Overcast",
    ]

    forecast = []
    for day_offset in range(7):
        date = today + timedelta(days=day_offset)
        variation = (day_offset * 1.3) % 5 - 2  # small daily variation

        point = WeatherDataPoint(
            date=date.strftime("%Y-%m-%d"),
            temperature_high=round(base_temp + variation + 5, 1),
            temperature_low=round(base_temp + variation - 4, 1),
            humidity=round(55 + (day_offset * 3.7) % 30, 1),
            precipitation_chance=round(max(0, 10 + (day_offset * 11) % 60), 1),
            condition=mock_conditions[day_offset % len(mock_conditions)],
        )
        forecast.append(point)

    return forecast


async def get_weather(city_name: str) -> list[WeatherDataPoint]:
    """Main entry point: fetch weather data, with automatic mock fallback.

    Called by the weather_fetcher node in the agent graph.
    """
    if settings.USE_MOCK_WEATHER:
        return generate_mock_weather(city_name)

    try:
        return await fetch_weather_live(city_name)
    except Exception:
        # Network issues, API downtime, etc. — degrade gracefully
        return generate_mock_weather(city_name)
