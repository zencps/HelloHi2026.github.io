import os

from dotenv import load_dotenv

from weather_app.interface import WeatherDashboard

YOUR_API_KEY_HERE = ""

load_dotenv() 


def resolve_api_key() -> str:
    """Return the best available API key."""
    from_env = os.getenv("OPENWEATHER_API_KEY", "").strip()
    return from_env or YOUR_API_KEY_HERE.strip()


def main() -> None:
    app = WeatherDashboard(api_key=resolve_api_key())
    app.mainloop()


if __name__ == "__main__":
    main()
