import requests

API_URL = "https://api.openweathermap.org/data/2.5/weather"
TIMEOUT_SECONDS = 10


class WeatherAPIError(Exception):
    """City not found, network down, unexpected response, etc."""


class MissingAPIKeyError(Exception):
    """No API key was supplied to get_weather()."""


def get_weather(city: str, api_key: str) -> dict:
    """Fetch live weather for *city* and return a normalised dictionary.

    This is the single function the GUI calls; everything below it
    (HTTP, status-code handling, JSON parsing) is private to the engine.
    """
    if not api_key or not api_key.strip():
        raise MissingAPIKeyError(
            "No API key configured.\n\n"
            "Create a free key at https://openweathermap.org/api and put "
            "OPENWEATHER_API_KEY=<your key> in the .env file next to main.py."
        )

    params = {
        "q": city.strip(),
        "appid": api_key.strip(),
        "units": "metric", 
    }

    try:
        response = requests.get(API_URL, params=params, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.RequestException as exc:
        raise WeatherAPIError(
            f"Network error - please check your connection.\n({exc})"
        ) from exc

    if response.status_code == 404:
        raise WeatherAPIError(
            "City not found. Please check the spelling and try again."
        )
    if response.status_code == 401:
        raise WeatherAPIError(
            "Invalid API key. Check OPENWEATHER_API_KEY in your .env file "
            "(brand-new keys can take up to ~2 hours to activate)."
        )
    if response.status_code != 200:
        raise WeatherAPIError(
            f"Unexpected server error (HTTP {response.status_code})."
        )

    try:
        data = response.json()
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": str(data["weather"][0]["description"]).capitalize(),
            "condition_id": int(data["weather"][0]["id"]),
        }
    except (KeyError, IndexError, ValueError, TypeError) as exc:
        raise WeatherAPIError("Could not understand the server response.") from exc
