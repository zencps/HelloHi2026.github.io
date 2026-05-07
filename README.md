# Python Weather Dashboard

A lightweight desktop weather app built with Python and Tkinter.
Type a city name, press **Search**, and see the current temperature,
humidity, wind speed, and description -- with an emoji icon and
background colour that change based on the live weather conditions.

Data comes from the free [OpenWeatherMap](https://openweathermap.org/api)
Current Weather API.

## Features

- Real-time weather for any city worldwide
- Large centred temperature readout, plus humidity, wind speed, and feels-like
- Dynamic emoji + colour theme per condition (sun, rain, snow, thunderstorm...)
- Friendly error handling: "City not found", invalid key, offline, etc.
- Press **Enter** in the search box as a shortcut for the Search button

## Project structure

```
python-weather-dashboard/
|
|-- .gitignore            Ignores .env (your private key) and cache files
|-- README.md             This file
|-- requirements.txt      requests + python-dotenv
|
|-- weather_app/
|   |-- __init__.py       Package marker
|   |-- api_client.py     The Engine: OpenWeatherMap API calls
|   `-- interface.py      The View: GUI, styling, dynamic themes
|
`-- main.py               Launch script (wires key -> view -> engine)
```

## 1. Get a free API key

1. Sign up at <https://home.openweathermap.org/users/sign_up> (the free plan is enough).
2. Confirm your email, then open the **API keys** tab:
   <https://home.openweathermap.org/api_keys>
3. Copy your default key. Note: brand-new keys can take up to ~2 hours to activate.

## 2. Install dependencies

```bash
cd python-weather-dashboard

python -m venv .venv              # optional but recommended
.venv\Scripts\activate            # Windows   (source .venv/bin/activate on macOS/Linux)

pip install -r requirements.txt
```

## 3. Add your API key

**Option A (recommended):** create a file named `.env` next to `main.py`:

```
OPENWEATHER_API_KEY=paste-your-key-here
```

`.env` is already listed in `.gitignore`, so your key will never be committed.

**Option B:** paste the key into the `YOUR_API_KEY_HERE = ""` constant in `main.py`.

## 4. Run the app

```bash
python main.py
```

Then type a city (e.g. `London`) and click **Search**.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| "Invalid API key" | New keys need up to ~2 hours; double-check `.env`. |
| "City not found" | Check spelling, or use `"City,CountryCode"` e.g. `Paris,FR`. |
| No window appears | Reinstall Python from python.org (includes Tkinter). |
| Network error | Check your internet connection / firewall / proxy. |

## Units

The app uses metric units (Celsius, m/s). For Fahrenheit and mph, change
`"units": "metric"` to `"units": "imperial"` in `weather_app/api_client.py`.
