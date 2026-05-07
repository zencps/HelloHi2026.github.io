"""main.py -- Entry point of the Weather Dashboard.

Wiring overview:
    1. Load the OpenWeatherMap key (priority: .env -> environment -> constant).
    2. Hand that key to the View (weather_app.interface.WeatherDashboard).
    3. Every time the user searches, the View pulls live data through the
       Engine (weather_app.api_client.get_weather) and paints the result.
"""

import os

from dotenv import load_dotenv

from weather_app.interface import WeatherDashboard

# --------------------------------------------------------------------------- #
#  Option B: paste your key directly into this constant.
#  Prefer the .env file (Option A) so the key never lands in git history.
# --------------------------------------------------------------------------- #
YOUR_API_KEY_HERE = ""

load_dotenv()  # reads the local .env file next to this script (if present)


def resolve_api_key() -> str:
    """Return the best available API key."""
    from_env = os.getenv("OPENWEATHER_API_KEY", "").strip()
    return from_env or YOUR_API_KEY_HERE.strip()


def main() -> None:
    app = WeatherDashboard(api_key=resolve_api_key())
    app.mainloop()


if __name__ == "__main__":
    main()
